# OpenVPN Client Generator

OpenVPN 클라이언트 인증서 및 설정 파일(.ovpn)을 자동으로 생성하는 Python 스크립트입니다.

## 📋 기능

- 여러 사용자의 클라이언트 인증서 및 개인 키 자동 생성
- 개별 사용자별 .ovpn 파일 생성
- 기존 인증서 중복 생성 방지
- 자동 오류 처리 및 로깅
- 템플릿 기반 설정 파일 생성

## 🚀 사용법

### 1. 준비물

다음 파일들이 필요합니다:

1. **Easy-RSA 파일**: [Easy-RSA 3.1.7](https://github.com/OpenVPN/easy-rsa/releases) 다운로드
2. **OVPN 템플릿 파일**: 서버 설정이 포함된 기본 .ovpn 파일
3. **이 스크립트**: `ovpn_generator.py`

### 2. 디렉토리 구조

```
project-root/
├── ovpn_generator.py
├── EasyRSA-3.1.7_final/
│   ├── easyrsa
│   ├── pki/
│   │   ├── ca.crt
│   │   ├── ovpn/
│   │   │   └── downloaded-client-config.ovpn  # 템플릿 파일
│   │   ├── issued/      # 생성된 인증서들
│   │   └── private/     # 생성된 개인 키들
│   └── ...
```

### 3. 설정

스크립트 상단의 설정을 수정하세요:

```python
# Easy-RSA 디렉토리 경로
path = "./EasyRSA-3.1.7_final"

# 사용자 리스트 (원하는 사용자명으로 변경)
users = [
    "d",
    "s"
]

# OVPN 템플릿 파일 이름
template_file = "downloaded-client-config.ovpn"
```

### 4. 실행

```bash
python ovpn_generator.py
```

## 📁 출력

실행 후 다음과 같은 파일들이 생성됩니다:

```
EasyRSA-3.1.7_final/pki/
├── issued/
│   ├── kimhd6.crt
│   ├── sjpark.crt
│   └── skydoo19.crt
├── private/
│   ├── kimhd6.key
│   ├── sjpark.key
│   └── skydoo19.key
└── ovpn/
    ├── kimhd6.ovpn    # 완성된 클라이언트 설정 파일
    ├── sjpark.ovpn    # 완성된 클라이언트 설정 파일
    └── skydoo19.ovpn  # 완성된 클라이언트 설정 파일
```

## 📝 OVPN 템플릿 예시

`downloaded-client-config.ovpn` 파일은 다음과 같은 형식이어야 합니다:

```
client
dev tun
proto udp
remote YOUR_SERVER_IP 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca [inline]
cert [inline]
key [inline]
remote-cert-tls server
cipher AES-256-CBC
verb 3

<ca>
-----BEGIN CERTIFICATE-----
[CA 인증서 내용]
-----END CERTIFICATE-----
</ca>
```

## ⚙️ 요구사항

- Python 3.6+
- Easy-RSA 3.x
- Linux/macOS 환경 (Windows의 경우 WSL 권장)

## 🔧 문제 해결

### 권한 오류
```bash
chmod +x EasyRSA-3.1.7_final/easyrsa
```

### 타임아웃 설정 변경
스크립트 상단의 `TIMEOUT` 값을 조정하세요:
```python
TIMEOUT = 120  # 2분으로 증가
```

### 템플릿 파일 인코딩 문제
템플릿 파일이 UTF-8로 인코딩되어 있는지 확인하세요.

## 🚨 주의사항

- 이 스크립트는 패스워드 없는 클라이언트 키를 생성합니다 (`nopass` 옵션)
- 기존 인증서가 있는 경우 덮어쓰지 않습니다
- 생성된 키와 인증서는 안전하게 보관하세요

## 📄 라이선스

MIT License

## 🤝 기여

이슈 리포트나 Pull Request는 언제나 환영합니다!

## 📞 지원

문제가 발생하면 GitHub Issues를 통해 문의해주세요.
