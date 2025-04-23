from string import Template
from typing import Optional

def create_html_template(main_content: str, subheading: str = "") -> str:
    """Creates HTML email content with dynamic main content and subheading."""
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template</title>
    <style type="text/css">
        /* Reset styles */
        body {
            margin: 0;
            padding: 0;
            min-width: 100%;
            width: 100% !important;
            height: 100% !important;
        }
        
        body, table, td, div, p, a {
            -webkit-font-smoothing: antialiased;
            text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
            line-height: 100%;
        }
        
        table, td {
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
            border-collapse: collapse !important;
            border-spacing: 0;
        }
        
        img {
            border: 0;
            line-height: 100%;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
        }
        
        /* Main styles */
        body {
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
        }
        
        .wrapper {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .content {
            background-color: #ffffff;
            padding: 40px;
        }
        
        .header {
            padding: 20px;
            text-align: center;
        }
        
        .footer {
            padding: 20px;
            text-align: center;
            color: #666666;
            font-size: 12px;
        }
        
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #007bff;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }
        
        /* Mobile styles */
        @media screen and (max-width: 600px) {
            .wrapper {
                width: 100% !important;
            }
            
            .content {
                padding: 20px !important;
            }
        }
    </style>
</head>
<body>
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
        <tr>
            <td>
                <div class="wrapper">
                    <!-- Header -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td class="header">
                                <img src="/api/placeholder/200/50" alt="Logo" width="200" height="50">
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Content -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td class="content">
                                <h1 style="color: #333333; font-size: 24px; margin-bottom: 20px;">Welcome!</h1>
                                <p style="color: #666666; font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
                                    ${main_content}
                                </p>
                                <h1>${subheading}</h1>
                                <a href="#" class="button">Call to Action</a>
                                <p style="color: #666666; font-size: 16px; line-height: 1.5;">
                                    Best regards,<br>
                                    Your Heal Seek 
                                </p>
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Footer -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td class="footer">
                                <p>© 2024 Your Company Name. All rights reserved.</p>
                                <p>
                                    You received this email because you signed up for updates from our company.<br>
                                    <a href="#" style="color: #666666;">Unsubscribe</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return Template(html_template).safe_substitute(
        main_content=main_content,
        subheading=subheading
    )