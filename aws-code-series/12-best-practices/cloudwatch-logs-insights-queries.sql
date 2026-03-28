-- ビルド失敗のログを検索
fields @timestamp, @message
| filter @message like /ERROR|FAIL|Exception/
| sort @timestamp desc
| limit 50

-- ビルド時間の統計
fields @timestamp, @message
| filter @message like /Build completed/
| stats count() as builds, 
        avg(@duration) as avg_duration,
        max(@duration) as max_duration
  by bin(1d)

-- 特定のフェーズでのエラー
fields @timestamp, @message
| filter @message like /Phase complete.*Status.*FAILED/
| sort @timestamp desc
