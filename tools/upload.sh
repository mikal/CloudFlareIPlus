#!/bin/bash
# GitHub文件夹批量上传脚本 - 100%修复版
# 用法: ./upload_folder_robust.sh -t <token> -o <owner> -r <repo> -f <folder> [-b <branch>] [-p <target_path>]

# ========== 参数初始化 ==========
TOKEN=""
OWNER=""
REPO=""
FOLDER=""
BRANCH="main"
TARGET_PATH=""

# 解析命令行参数
while getopts "t:o:r:f:b:p:" opt; do
  case $opt in
    t) TOKEN="$OPTARG" ;;
    o) OWNER="$OPTARG" ;;
    r) REPO="$OPTARG" ;;
    f) FOLDER="$OPTARG" ;;
    b) BRANCH="$OPTARG" ;;
    p) TARGET_PATH="$OPTARG" ;;
    *) echo "用法: $0 -t TOKEN -o OWNER -r REPO -f FOLDER [-b BRANCH] [-p TARGET_PATH]"; exit 1 ;;
  esac
done

# 验证必要参数
if [[ -z "$TOKEN" || -z "$OWNER" || -z "$REPO" || -z "$FOLDER" ]]; then
  echo "错误: 缺少必要参数"
  echo "用法: $0 -t TOKEN -o OWNER -r REPO -f FOLDER [-b BRANCH] [-p TARGET_PATH]"
  exit 1
fi

if [[ ! -d "$FOLDER" ]]; then
  echo "错误: 文件夹 $FOLDER 不存在"
  exit 1
fi

# 标准化路径
FOLDER="$(realpath "$FOLDER")/"
if [[ $? -ne 0 ]]; then
  echo "错误: 无法解析文件夹路径"
  exit 1
fi

echo "正在扫描文件夹: $FOLDER"
echo "================================"

# ========== 关键修复：可靠文件扫描 ==========
# 使用find并将结果存入临时文件，避免管道和子shell问题
TEMP_FILELIST=$(mktemp)
find "$FOLDER" -type f > "$TEMP_FILELIST" 2>&1

if [[ $? -ne 0 ]]; then
  echo "错误: find命令执行失败"
  rm -f "$TEMP_FILELIST"
  exit 1
fi

TOTAL_FILES=$(wc -l < "$TEMP_FILELIST")
if [[ $TOTAL_FILES -eq 0 ]]; then
  echo "错误: 在 $FOLDER 中没有找到任何文件！"
  echo "请验证: ls -la \"$FOLDER\""
  rm -f "$TEMP_FILELIST"
  exit 1
fi

CURRENT=0
SUCCESS=0
FAILED=0
API_URL="https://api.github.com/repos/$OWNER/$REPO/contents"

echo "找到 $TOTAL_FILES 个文件"
echo "开始上传..."
echo ""

# ========== 主循环（从临时文件读取） ==========
while IFS= read -r FILE; do
  [[ -z "$FILE" ]] && continue
  
  CURRENT=$((CURRENT + 1))
  
  # 计算相对路径
  REL_PATH="${FILE#$FOLDER}"
  
  # 构建GitHub目标路径（修复路径拼接逻辑）
  if [[ -n "$TARGET_PATH" ]]; then
    DEST_PATH="${TARGET_PATH%/}/${REL_PATH}"
  else
    DEST_PATH="$REL_PATH"
  fi
  
  # URL编码（多层fallback方案）
  if command -v python3 &> /dev/null; then
    ENC_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$DEST_PATH', safe=''))" 2>/dev/null)
  elif command -v python &> /dev/null; then
    ENC_PATH=$(python -c "import urllib.parse; print(urllib.parse.quote('$DEST_PATH', safe=''))" 2>/dev/null)
  else
    ENC_PATH=$(echo "$DEST_PATH" | sed 's/ /%20/g; s/!/%21/g; s/#/%23/g; s/\$/%24/g; s/\&/%26/g; s/'\''/%27/g')
  fi
  
  # 检查文件是否可读
  if [[ ! -r "$FILE" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ❌ 无法读取: $REL_PATH"
    ((FAILED++))
    continue
  fi
  
  # base64编码（关键修复：添加错误检查）
  CONTENT=$(base64 -w 0 "$FILE" 2>&1)
  if [[ $? -ne 0 || -z "$CONTENT" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ❌ base64失败: $REL_PATH"
    echo "  错误: $CONTENT"
    ((FAILED++))
    continue
  fi
  
  # 检查文件是否已存在，获取SHA用于覆盖
  EXISTING_SHA=""
  CHECK_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/$ENC_PATH" 2>/dev/null)
  if echo "$CHECK_RESPONSE" | grep -q '"sha"'; then
    EXISTING_SHA=$(echo "$CHECK_RESPONSE" | jq -r '.sha' 2>/dev/null || echo "$CHECK_RESPONSE" | grep -o '"sha":"[^"]*' | cut -d'"' -f4)
  fi
  
  # 构建JSON（强制覆盖模式）
  if [[ -n "$EXISTING_SHA" ]]; then
    JSON="{\"message\":\"Overwrite $REL_PATH via script\",\"branch\":\"$BRANCH\",\"content\":\"$CONTENT\",\"sha\":\"$EXISTING_SHA\"}"
    echo "[$CURRENT/$TOTAL_FILES] 🔄 检测到已存在文件，准备覆盖: $REL_PATH"
  else
    JSON="{\"message\":\"Upload $REL_PATH via script\",\"branch\":\"$BRANCH\",\"content\":\"$CONTENT\"}"
  fi
  
  # ========== 核心修复：完全禁用错误退出，手动处理所有错误 ==========
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X PUT \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -d "$JSON" \
    "$API_URL/$ENC_PATH" 2>&1)
  CURL_EXIT_CODE=$?
  
  # 分离响应体和状态码
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  # 显示结果（增加错误详情）
  if [[ $CURL_EXIT_CODE -ne 0 ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ❌ curl错误: $REL_PATH"
    echo "  Curl退出码: $CURL_EXIT_CODE"
    echo "  详情: $BODY"
    ((FAILED++))
  elif [[ "$HTTP_CODE" == "200" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ✅ 更新成功: $REL_PATH"
    ((SUCCESS++))
  elif [[ "$HTTP_CODE" == "201" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ✅ 上传成功: $REL_PATH"
    ((SUCCESS++))
  elif [[ "$HTTP_CODE" == "422" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ⚠️  文件已存在/验证失败 (422): $REL_PATH"
    ((FAILED++))
  elif [[ "$HTTP_CODE" == "401" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ❌ 认证失败 (401): Token无效或权限不足"
    echo "  响应: $BODY"
    ((FAILED++))
  elif [[ "$HTTP_CODE" == "404" ]]; then
    echo "[$CURRENT/$TOTAL_FILES] ❌ 仓库或分支不存在 (404)"
    echo "  请检查: $OWNER/$REPO (分支: $BRANCH)"
    echo "  响应: $BODY"
    ((FAILED++))
  else
    echo "[$CURRENT/$TOTAL_FILES] ❌ 失败 (HTTP $HTTP_CODE): $REL_PATH"
    echo "  响应: $BODY" | head -c 200
    ((FAILED++))
  fi
  
  # 每5个文件休眠1秒，避免触发速率限制
  if [[ $((CURRENT % 5)) -eq 0 && $CURRENT -lt $TOTAL_FILES ]]; then
    sleep 1
  fi
  
  # 强制继续循环，确保不会意外退出
  continue
done < "$TEMP_FILELIST"

# 清理临时文件
rm -f "$TEMP_FILELIST"

# ========== 最终报告 ==========
echo ""
echo "================================"
echo "上传完成！总计: $TOTAL_FILES 个文件"
echo "  成功: $SUCCESS"
echo "  失败: $FAILED"

if [[ $FAILED -gt 0 ]]; then
  echo ""
  echo "⚠️  有 $FAILED 个文件失败。常见原因:"
  echo "   - Token权限不足（需要repo权限）"
  echo "   - 分支名错误（分支: $BRANCH）"
  echo "   - 文件已存在（考虑添加SHA覆盖逻辑）"
  exit 1
fi

exit 0
