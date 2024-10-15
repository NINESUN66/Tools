@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set foundWLAN=false
echo 正在寻找本机WLAN IP地址。。。
for /f "delims=" %%a in ('ipconfig') do (
    rem 检查是否为WLAN适配器
    echo %%a | findstr /C:"WLAN" >nul
    if !errorlevel! equ 0 (
        set foundWLAN=true
    )
    rem 如果找到了WLAN且当前行有IPv4地址，则处理整行
    if "!foundWLAN!"=="true" (
        echo %%a | findstr /C:"IPv4 Address" >nul
        if !errorlevel! equ 0 (
            for /f "tokens=14 delims= " %%b in ("%%a") do (
                rem 去除前后空格
                set "cleanIP=%%b"
                set "cleanIP=!cleanIP: =!"
                rem 确保没有尾随的空格和回车
                echo|set /p=!cleanIP!|clip
            )
            goto :end
        )
    )
)
:end
