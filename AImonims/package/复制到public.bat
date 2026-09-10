@echo off
chcp 65001 >nul
echo ========================================
echo Live2D数字人完整包 - 自动复制脚本
echo ========================================
echo.
echo 正在复制Live2D核心库...
xcopy /E /Y /Q "live2d_core\*" "public\live2d_core\"
echo [完成] Live2D核心库

echo.
echo 正在复制chitose模型...
xcopy /E /Y /Q "chitose\*" "public\live2d_model\chitose\"
echo [完成] chitose模型

echo.
echo 正在复制HTML页面...
copy /Y /Q "live2d-page.html" "public\live2d-page.html"
copy /Y /Q "mmd-page.html" "public\mmd-page.html"
echo [完成] HTML页面

echo.
echo 正在复制Vue组件...
copy /Y /Q "Live2DAvatar.vue" "..\src\components\Live2DAvatar.vue"
echo [完成] Vue组件

echo.
echo ========================================
echo 复制完成！
echo.
echo 请查看 PUBLIC_FOLDER_README.txt 了解公共文件夹内容
echo 请查看 INTEGRATION_README.txt 了解集成步骤
echo ========================================
pause
