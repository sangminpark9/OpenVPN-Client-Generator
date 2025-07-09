import os
import subprocess
import sys

# 전체 작업의 타임아웃(초) 설정
TIMEOUT = 60  # 1분

# Easy-RSA 디렉토리 경로
path = "./EasyRSA-3.1.7_final"

# 인증서 및 OVPN 파일을 생성할 사용자 리스트
users = [
    "d"
]

# OVPN 템플릿 파일 경로 (공통 설정용)
template_file = "downloaded-client-config.ovpn"
template_path = f"{path}/pki/ovpn/{template_file}"

def check_dependencies():
    """필요한 디렉토리와 파일들이 존재하는지 확인"""
    if not os.path.exists(path):
        print(f"오류: Easy-RSA 디렉토리가 존재하지 않습니다: {path}")
        return False
        
    easyrsa_script = f"{path}/easyrsa"
    if not os.path.exists(easyrsa_script):
        print(f"오류: easyrsa 스크립트가 존재하지 않습니다: {easyrsa_script}")
        return False
    
    # OVPN 디렉토리 생성
    ovpn_dir = f"{path}/pki/ovpn"
    if not os.path.exists(ovpn_dir):
        os.makedirs(ovpn_dir)
        print(f"OVPN 디렉토리 생성: {ovpn_dir}")
    
    if not os.path.exists(template_path):
        print(f"경고: 템플릿 파일이 존재하지 않습니다: {template_path}")
        return False
    
    return True

def read_template():
    """템플릿 파일 읽기"""
    try:
        with open(template_path, "r", encoding='utf-8') as template:
            return template.readlines()
    except Exception as e:
        print(f"템플릿 파일 읽기 오류: {e}")
        return None

def create_certificates_and_keys():
    """클라이언트 인증서 및 키 생성"""
    success = True
    
    for user in users:
        # 이미 인증서가 존재하는지 확인
        cert_path = f"{path}/pki/issued/{user}.crt"
        key_path = f"{path}/pki/private/{user}.key"
        
        if os.path.exists(cert_path) and os.path.exists(key_path):
            print(f"✓ {user} 인증서가 이미 존재합니다.")
            continue
            
        print(f"🔑 {user} 인증서 생성 중...")
        
        # 사용자별 인증서 생성 명령어
        command = f"cd {path} && echo 'yes' | ./easyrsa build-client-full {user} nopass"

        try:
            # 명령어 실행
            result = subprocess.run(
                command,
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=TIMEOUT,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ {user} 인증서 생성 중 오류 발생 (exit code: {result.returncode})")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                success = False
            else:
                print(f"✅ {user} 인증서 생성 완료")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {user} 인증서 생성 중 타임아웃 발생")
            success = False
        except Exception as e:
            print(f"❌ {user} 인증서 생성 중 예외 발생: {e}")
            success = False

    return success

def read_cert_file(cert_path):
    """인증서 파일 읽기"""
    try:
        with open(cert_path, "r", encoding='utf-8') as crt:
            crt_strings = crt.readlines()
            
        # 인증서 시작 위치 찾기
        start_idx = -1
        for i, line in enumerate(crt_strings):
            if "-----BEGIN CERTIFICATE-----" in line:
                start_idx = i
                break
        
        if start_idx == -1:
            print(f"인증서 파일에서 시작 태그를 찾을 수 없습니다: {cert_path}")
            return None
            
        cert_lines = ["\n<cert>\n"] + crt_strings[start_idx:] + ["</cert>\n"]
        return cert_lines
        
    except Exception as e:
        print(f"인증서 파일 읽기 오류: {e}")
        return None

def read_key_file(key_path):
    """개인 키 파일 읽기"""
    try:
        with open(key_path, "r", encoding='utf-8') as key_file:
            key_strings = key_file.readlines()
            
        # 개인 키 시작 위치 찾기
        start_idx = -1
        for i, line in enumerate(key_strings):
            if "-----BEGIN PRIVATE KEY-----" in line:
                start_idx = i
                break
        
        if start_idx == -1:
            print(f"키 파일에서 시작 태그를 찾을 수 없습니다: {key_path}")
            return None
            
        key_lines = ["\n<key>\n"] + key_strings[start_idx:] + ["</key>\n"]
        return key_lines
        
    except Exception as e:
        print(f"키 파일 읽기 오류: {e}")
        return None

def create_ovpn_file(user, template_strings):
    """개별 사용자의 OVPN 파일 생성"""
    cert_path = f"{path}/pki/issued/{user}.crt"
    key_path = f"{path}/pki/private/{user}.key"
    ovpn_path = f"{path}/pki/ovpn/{user}.ovpn"
    
    # 파일 존재 확인
    if not os.path.exists(cert_path):
        print(f"❌ 인증서 파일이 존재하지 않습니다: {cert_path}")
        return False
        
    if not os.path.exists(key_path):
        print(f"❌ 키 파일이 존재하지 않습니다: {key_path}")
        return False
    
    # 이미 OVPN 파일이 존재하는지 확인
    if os.path.exists(ovpn_path):
        print(f"✓ {user}.ovpn 파일이 이미 존재합니다.")
        return True
    
    print(f"📝 {user}.ovpn 파일 생성 중...")
    
    # 인증서 읽기
    cert_lines = read_cert_file(cert_path)
    if not cert_lines:
        return False
    
    # 개인 키 읽기
    key_lines = read_key_file(key_path)
    if not key_lines:
        return False
    
    try:
        # </ca> 태그 찾기
        ca_end_index = -1
        for i, line in enumerate(template_strings):
            if "</ca>" in line:
                ca_end_index = i + 1
                break
        
        if ca_end_index == -1:
            print("템플릿 파일에서 </ca> 태그를 찾을 수 없습니다.")
            return False
        
        # OVPN 파일 작성
        with open(ovpn_path, "w", encoding='utf-8') as ovpn:
            # 템플릿의 CA 부분까지 복사
            ovpn.writelines(template_strings[:ca_end_index])
            
            # 인증서 추가
            ovpn.writelines(cert_lines)
            
            # 개인 키 추가
            ovpn.writelines(key_lines)
            
            # 추가 설정 (개행문자 추가)
            ovpn.write("\nreneg-sec 0\n")
        
        print(f"✅ {user}.ovpn 파일 생성 완료: {ovpn_path}")
        return True
        
    except Exception as e:
        print(f"❌ {user}.ovpn 파일 생성 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 OpenVPN 클라이언트 구성 파일 생성 스크립트")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        print("❌ 필수 파일이나 디렉토리가 없습니다.")
        sys.exit(1)
    
    # 템플릿 파일 읽기
    template_strings = read_template()
    if not template_strings:
        print("❌ 템플릿 파일을 읽을 수 없습니다.")
        sys.exit(1)
    
    # 인증서 및 키 생성
    print("\n🔐 인증서 및 키 생성 단계")
    print("-" * 30)
    
    if not create_certificates_and_keys():
        print("❌ 일부 인증서 생성에 실패했습니다.")
        print("⚠️  그래도 기존 인증서로 OVPN 파일 생성을 시도합니다.")
    
    # OVPN 파일 생성
    print("\n📄 OVPN 파일 생성 단계")
    print("-" * 30)
    
    success_count = 0
    for user in users:
        if create_ovpn_file(user, template_strings):
            success_count += 1
    
    print(f"\n🎉 결과: {success_count}/{len(users)} 개의 OVPN 파일 생성 완료")
    
    if success_count == len(users):
        print("✅ 모든 사용자의 OVPN 파일이 성공적으로 생성되었습니다!")
    else:
        print("⚠️  일부 파일 생성에 실패했습니다. 로그를 확인하세요.")

if __name__ == "__main__":
    main()
