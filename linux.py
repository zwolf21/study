*서버 설정
-yum 원본 패키지만 설치 됨
vi /etc/yum.repos.d/CentOS-Base.repo
[updates] 부분 이하 주석처리 #
#[update]
# ...
# ...

-IP 주소 설정
vi /etc/sysconfig/network-scripts/ifcfg-eno16777728

BOOTPROTO=none  ->'dhcp' 에서 none으로 수정
나머지 4개 추가
IPADDR=192.168.111.100 
NETMASK=255.255.255.0
GATEWAY=192.168.111.2
DNS1=192.168.111.2
:wq

systemctl restart network
ip addr -> ip정보 확인

-SElinux 끄기(서버환경과 충돌 가능성)
vi /etc/sysconfig/selinux

SELINUX=enforcing -> 
SELINUX=disabled
:wq

*클라이언트 설정
-root사용자로 처음에 로그인 못하게 하기
vi /etc/pam.d/gdm-password
다음한줄 추가
auth	required	pam_succeed_if.so 	user	!= root quiet







*네임서버 개요
네임서버=DNS(Domain Name Server)
도메인 이름을 IP 주소로 변환시켜 주는 역할(Name Resolution)
예) wwww.nate.com -> 211.234.241.204

1.hosts 파일을 이용하여 네트워크 접속
hosts 파일에 URL과 IP주소를 기록해 놓는 방식 사용
	windows - C:\Windwos\System32\drivers\etc\hosts
	Linux	- /etc/hosts

2.네임서버를 이용하여 네트워크 접속
이름 해석(Name Resolution)을 전문적으로 해 주는 서버 컴퓨터
전화 안내 114와 같은 역할
네임서버는 인터넷에서 변화하는 모든 컴퓨터의 URL과 IP정보를 거의 실시간으로 제공하므로, 사용자는 더 이상 URL에 해당하는 IP주소를 신경
쓸 필요가 없어짐

네임서버 설정 파일 위치 -hosts 파일에서 url 먼저 검색 해보고 없으면 찾는 곳
/etc/resolv.conf 

-캐싱전용 네임서버 구축(192.168.111.128)-상위 dns서버에서 물어옴
1)bind, bind-chroot 패키지 설치
 yum -y install bind bind-chroot
2)/etc/named.conf 파일 
 options - listen-on port 53 {127.0.0.1;} -> listen-on port 53 { any;}
 		   listen-on-v6 port 53 { ::1; } -> listen-on-v6 port 53 { none; }
 		   allow-query {localhost;} -> allow-query {any;}
3)systemctl restart named
4)systemctl enable named (껏다 켜도 항시 동작)
5)방화벽으로 서비스 포트 개방
 firewall-config -> 설정:영구적 -> 서비스:dns체크 -> 옵션:firewalld 다시불러오기
6)클라이언트 테스트
 클라이언트의 DNS 서버를 위에서 구축한 네임서버로 설정한다
 클라이언트 /etc/resolv.conf 의 nameserver 항목을 192.168.111.128 로 설정
 윈도우 클라이언트의 경우 cmd(관리자) 에서
 netsh interface show interface 로 인터페이스 이름 확인
 netsh interface ip set dns name="인터페이스이름" source=static addr=192.168.111.128
 원래대로 -> netsh interface ip set dns "인터페이스이름" dhcp

 -마스터 네임서버의 구축 -도메인에 속해있는 컴퓨터들의 이름관리, 외부에 해당 컴퓨터의 IP주소를 알려주는 역할
  ex)nate.com 네임서버
1)테스트용 간단한 웹서버 구현
	systemctl restart httpd
	firewall-config -> http open
	/var/www/html/index.html 간단히 작성 ---> <h1>Centos</h2> (www.centos.com 으로 접속시 보여줄 화면)

2)ftp서버 설치
	yum -y install vsftpd
    firewall-cmd --permanent --add-service=ftp (firewall-config는 xwindow있을때만)
    firewall-cmd --reload (***text모드 에서 firewall 사용법***)
3)/etc/named.conf 파일에 도메인 관리항목 zone 추가
zone "contos.com"  IN {
	type master;
	file "centos.com.db";
	allow-update { none; };
};
4)named.conf 파일에 zone 추가 후 named-checkconf 로 설정 변경 확인
5)/var/named 폴더에 centos.com.db 파일 만듬 vi /var/named/centos.com.db
6)centos.com.db 의 내용을 작성
$TTL	3H
@		SOA		@		root		( 2 1D 1H 1W 1H )
		IN 		NS 		@
		IN 		A 		192.168.111.128 

www 	IN 		A 		192.168.111.128  ----> www.centos.com 의 주소를 알려줌
ftp 	IN 		A 		192.168.111.128  ----> ftp.centos.com 의 주소를 알려줌

7)centos.com.db의 설정확인 named-checkzone centos.com centos.com.db
8)systemctl restart named
































 

