def message(domain, uidb, token): 
    return f"아래 링크를 클릭하면 학교 이메일 인증이 완료됩니다.\n\n회원가입 링크 : http://{domain}/activate/{uidb}/{token}\n\n감사합니다."
