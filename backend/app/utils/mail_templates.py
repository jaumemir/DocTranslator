# app/utils/mail_templates.py
from datetime import datetime

def generate_register_email(user: dict, code: str) -> str:
    """Generate registration verification code email HTML template"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DocTranslator - 注册验证码</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background-color: #f8fafc;
                color: #334155;
                line-height: 1.6;
            }}

            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }}

            .header {{
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                padding: 40px 30px;
                text-align: center;
                position: relative;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                pointer-events: none;
            }}



            .brand-name {{
                color: white;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
            }}

            .header-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
            }}

            .content {{
                padding: 40px 30px;
            }}

            .welcome-text {{
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 16px;
            }}

            .instruction-text {{
                color: #64748b;
                margin-bottom: 32px;
            }}

            .code-container {{
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border: 2px solid #0ea5e9;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                margin: 32px 0;
                position: relative;
            }}

            .code-label {{
                font-size: 12px;
                color: #0369a1;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            }}

            .verification-code {{
                font-size: 36px;
                font-weight: 700;
                color: #0c4a6e;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
                background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}

            .security-notice {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 16px;
                border-radius: 8px;
                margin: 24px 0;
            }}

            .security-notice p {{
                color: #92400e;
                font-size: 14px;
                margin: 0;
            }}

            .footer {{
                background: #f8fafc;
                padding: 24px 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}

            .footer-text {{
                color: #94a3b8;
                font-size: 14px;
            }}

            .footer-link {{
                color: #3b82f6;
                text-decoration: none;
                font-weight: 500;
            }}

            @media only screen and (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 12px;
                }}

                .header, .content, .footer {{
                    padding: 30px 20px;
                }}

                .verification-code {{
                    font-size: 28px;
                    letter-spacing: 6px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="brand-name">DocTranslator</div>
                <div class="header-subtitle">AI智能文档翻译</div>
            </div>

            <div class="content">
                <h2 class="welcome-text">欢迎使用DocTranslator！</h2>
                <p class="instruction-text">
                    尊敬的用户,感谢您注册DocTranslator。请使用以下验证码完成邮箱验证：
                </p>

                <div class="code-container">
                    <div class="code-label">验证码</div>
                    <div class="verification-code">{code}</div>
                </div>

                <div class="security-notice">
                    <p>⚠️ 安全提醒：验证码有效期为 15 分钟，请勿泄露给他人。如非本人操作，请忽略此邮件。</p>
                </div>

                <p style="text-align: center; color: #64748b; font-size: 14px;">
                    如果您有任何问题，请联系我们
                </p>
            </div>

            <div class="footer">
                <p class="footer-text">
                    此邮件由系统自动发送，请勿回复。<br>
                    © 2025 DocTranslator. 保留所有权利。<br>
                    <a href="https://www.doctranslator.cn" class="footer-link">访问官网</a> 
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def generate_reset_password_email(user: dict, code: str) -> str:
    """Generate password reset verification code email HTML template"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DocTranslator - 密码重置验证码</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background-color: #f8fafc;
                color: #334155;
                line-height: 1.6;
            }}

            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }}

            .header {{
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                padding: 40px 30px;
                text-align: center;
                position: relative;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                pointer-events: none;
            }}

            .reset-icon {{
                width: 48px;
                height: 48px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                margin: 0 auto 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
            }}

            .brand-name {{
                color: white;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
            }}

            .header-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
            }}

            .content {{
                padding: 40px 30px;
            }}

            .reset-text {{
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 16px;
            }}

            .instruction-text {{
                color: #64748b;
                margin-bottom: 32px;
            }}

            .code-container {{
                background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                border: 2px solid #ef4444;
                border-radius: 12px;
                padding: 24px 16px;
                text-align: center;
                margin: 32px 0;
                position: relative;
                overflow: hidden;
            }}

            .code-label {{
                font-size: 12px;
                color: #991b1b;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 16px;
            }}

            .verification-code {{
                font-size: 32px;
                font-weight: 700;
                color: #7f1d1d;
                letter-spacing: 6px;
                font-family: 'Courier New', 'SF Mono', Monaco, 'Consolas', monospace;
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;

                /* 防止换行 */
                white-space: nowrap;
                word-break: keep-all;
                display: inline-block;
                max-width: 100%;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            .security-notice {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 16px;
                border-radius: 8px;
                margin: 24px 0;
            }}

            .security-notice p {{
                color: #92400e;
                font-size: 14px;
                margin: 0;
            }}

            .steps-container {{
                background: #f8fafc;
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
            }}

            .step-item {{
                display: flex;
                align-items: flex-start;
                margin-bottom: 16px;
            }}

            .step-item:last-child {{
                margin-bottom: 0;
            }}

            .step-number {{
                width: 24px;
                height: 24px;
                background: #ef4444;
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 600;
                margin-right: 12px;
                flex-shrink: 0;
            }}

            .step-text {{
                flex: 1;
                font-size: 14px;
                color: #475569;
            }}

            .footer {{
                background: #f8fafc;
                padding: 24px 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}

            .footer-text {{
                color: #94a3b8;
                font-size: 14px;
            }}

            .footer-link {{
                color: #3b82f6;
                text-decoration: none;
                font-weight: 500;
            }}

            /* 移动端优化 */
            @media only screen and (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 12px;
                }}

                .header, .content, .footer {{
                    padding: 30px 20px;
                }}

                .reset-text {{
                    font-size: 18px;
                }}

                .instruction-text {{
                    font-size: 14px;
                }}

                .code-container {{
                    padding: 20px 12px;
                    margin: 24px 0;
                }}

                .verification-code {{
                    font-size: 24px;
                    letter-spacing: 4px;
                }}

                .code-label {{
                    font-size: 11px;
                    margin-bottom: 12px;
                }}

                .steps-container {{
                    padding: 16px;
                }}

                .step-item {{
                    margin-bottom: 12px;
                }}
            }}

            /* 超小屏幕适配 */
            @media only screen and (max-width: 400px) {{
                .verification-code {{
                    font-size: 20px;
                    letter-spacing: 2px;
                }}

                .code-container {{
                    padding: 16px 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="brand-name">DocTranslator Pro</div>
                <div class="header-subtitle">AI智能文档翻译</div>
            </div>

            <div class="content">
                <h2 class="reset-text">密码重置请求</h2>
                <p class="instruction-text">
                    尊敬的用户，我们收到了您的密码重置请求。请使用以下验证码来完成密码重置：
                </p>

                <div class="code-container">
                    <div class="code-label">密码重置验证码</div>
                    <div class="verification-code">{code}</div>
                </div>

                <!-- 重置步骤说明 -->
                <div class="steps-container">
                    <div class="step-item">
                        <div class="step-number">1</div>
                        <div class="step-text">返回密码重置页面</div>
                    </div>
                    <div class="step-item">
                        <div class="step-number">2</div>
                        <div class="step-text">输入此验证码</div>
                    </div>
                    <div class="step-item">
                        <div class="step-number">3</div>
                        <div class="step-text">设置您的新密码</div>
                    </div>
                </div>

                <div class="security-notice">
                    <p>⚠️ 安全提醒：验证码有效期为 15 分钟，请勿泄露给他人。如非本人操作，请立即联系客服。</p>
                </div>

                <p style="text-align: center; color: #64748b; font-size: 14px;">
                    如果您没有请求密码重置，请忽略此邮件
                </p>
            </div>

            <div class="footer">
                <p class="footer-text">
                    此邮件由系统自动发送，请勿回复。<br>
                    © 2025 DocTranslator 保留所有权利。<br>
                    <a href="https://www.doctranslator.cn" class="footer-link">访问官网</a>

                </p>
            </div>
        </div>
    </body>
    </html>
    """


def generate_new_user_notification(user: dict) -> str:
    """Generate new user registration notification email HTML"""
    return f"""
    <html>
      <style>
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 10px 0; }}
      </style>
      <body>
        <div class="container">
          <h2>系统通知：新用户注册</h2>
          <p>以下用户刚刚完成了注册：</p>
          <ul>
            <li>用户ID：{user.get('id', '')}</li>
            <li>邮箱：{user.get('email', '')}</li>
            <li>注册时间：{user.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</li>
          </ul>
        </div>
      </body>
    </html>
    """

def generate_password_reset_email(user: dict, code: str) -> str:
    """Generate password reset email HTML"""
    return f"""
    <html>
      <style>
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; }}
        .code {{ color: #007bff; font-size: 32px; text-align: center; }}
      </style>
      <body>
        <div class="container">
          <h2>密码重置验证码</h2>
          <p>您的密码重置验证码是：</p>
          <div class="code">{code}</div>
          <p>验证码有效期30分钟</p>
        </div>
      </body>
    </html>
    """

def generate_password_change_email(user: dict) -> str:
    """Generate password change notification email HTML"""
    return f"""
    <html>
      <style>
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; }}
      </style>
      <body>
        <div class="container">
          <h2>密码修改通知</h2>
          <p>您的账户 {user.get('email', '')} 密码修改成功</p>
          <p>时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
      </body>
    </html>
    """