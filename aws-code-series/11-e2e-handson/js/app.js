document.addEventListener('DOMContentLoaded', function() {
    // デプロイ時刻を表示
    document.getElementById('deploy-time').textContent = new Date().toLocaleString('ja-JP');
});
