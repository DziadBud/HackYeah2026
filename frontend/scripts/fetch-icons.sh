#!/usr/bin/env bash
# re-downloads the self-hosted material symbols subset after adding an icon.
# add the glyph name below (any order), run from frontend/: ./scripts/fetch-icons.sh
set -euo pipefail
ICONS="account_balance add_circle arrow_back bar_chart download star trending_down trending_flat trending_up play_circle add_comment apartment arrow_forward attach_file auto_awesome call chat_bubble chevron_right close contrast face_6 favorite flaky format_size forum groups holiday_village home how_to_reg info lightbulb login logout mail menu mic notifications notifications_active person photo_camera place psychology reply report_problem schedule school search search_check send sentiment_very_satisfied smart_toy stop_circle support_agent thumb_up verified verified_user volume_up"
names=$(printf '%s\n' $ICONS | sort | paste -sd, -)
ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
css=$(curl -fsS -A "$ua" "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0..1,0&icon_names=$names&display=block")
url=$(grep -oE 'https://[^)]+' <<<"$css")
curl -fsS -o app/fonts/material-symbols-outlined.woff2 "$url"
echo "saved $(wc -c < app/fonts/material-symbols-outlined.woff2) bytes"
