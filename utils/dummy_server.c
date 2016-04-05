#include <windows.h>
#define PORT 6666

int main() {
	WSADATA trash;
	WSAStartup(MAKEWORD(2,2),&trash);
	struct sockaddr_in addr={ .sin_family=AF_INET, .sin_port=htons(PORT), .sin_addr.s_addr=INADDR_ANY };
	int sock=socket(PF_INET,SOCK_STREAM,0);
	bind(sock,(struct sockaddr *)&addr,sizeof(addr));
	listen(sock,1);
	accept(sock,NULL,NULL);
	write(sock,"ciao",4);
}
