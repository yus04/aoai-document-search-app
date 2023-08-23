# Pythonスクリプトの実行
$pythonExe = "python"  # Pythonの実行可能ファイルへのパスを指定する場合は変更してください

# 各Pythonファイルのパス
$scripts = @(
    ".\app\prepdocs\create_and_upload_blob.py",
    ".\app\prepdocs\create_datasource.py",
    ".\app\prepdocs\create_skillset.py",
    ".\app\prepdocs\create_index.py",
    ".\app\prepdocs\create_indexer.py"
)

# 各Pythonスクリプトを順番に実行
foreach ($script in $scripts) {
    Write-Host "Executing $script..."
    & $pythonExe $script
    Write-Host "$script execution completed."
}
