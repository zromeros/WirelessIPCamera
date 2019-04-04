#include "wc_esp32_socket.h"

DRAM_ATTR QueueHandle_t xQueue_to_camera = NULL;
// Spi buffer
DRAM_ATTR char socket_data_to_server_tcp[QUEUE_TO_SERVER_MQTT_LENGTH]="";
DRAM_ATTR char socket_data_to_server_udp[QUEUE_TO_SERVER_UDP_LENGTH]="";
DRAM_ATTR char socket_data_to_camera[SIZE_DATA_TO_CAMERA]="";

//DRAM_ATTR QueueHandle_t xQueue_to_camera_tcp = NULL;


/* SOCKET TO SEND A COMMAND OVER TCP */
void socket_tcp_tx(char * data){
	while(false == connected){
		vTaskDelay(2000 / portTICK_RATE_MS);
	}

    sock_tcp_tx = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
   	if (sock_tcp_tx < 0) {
   		ESP_LOGI(TAG_SOCKET, "CREATE SOCKET STATUS: %s", strerror(errno));
   		close(sock_tcp_tx);
   	}

    memset(&tcp_tx_address, 0, sizeof(struct sockaddr_in));
    tcp_tx_address.sin_family = AF_INET;
    tcp_tx_address.sin_addr.s_addr = inet_addr(SERVER_ADDRESS);
    tcp_tx_address.sin_port = htons(SOCKET_PORT_TCP_TX);

	if(connect(sock_tcp_tx,(struct sockaddr *)&tcp_tx_address,sizeof(struct sockaddr_in)) == 0){
		if(send(sock_tcp_tx, data, strlen(data), 0) > -1){
			ESP_LOGI(TAG_SOCKET, "Data sent: %s", data);
			send(sock_tcp_tx, data, strlen(data), 0);
			close(sock_tcp_tx);
		}
		else{
			ESP_LOGI(TAG_SOCKET, "Error to send: %s", data);
			close(sock_tcp_tx);
		}
	}
}

///* SOCKET TCP RECEIVE CONFIGURATION */
//void socket_tcp_rx_cfg(void){
//	while(false == connected){
//		vTaskDelay(2000 / portTICK_RATE_MS);
//	}
//
//    sock_tcp_rx = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
//   	if (sock_tcp_tx < 0) {
//   		ESP_LOGI(TAG_SOCKET, "CREATE SOCKET STATUS: %s", strerror(errno));
//   		close(sock_tcp_rx);
//   	}
//
//   	memset(&tcp_rx_address, 0, sizeof(struct sockaddr_in));
//   	tcp_rx_address.sin_family = AF_INET;
//   	tcp_rx_address.sin_addr.s_addr = SOCKET_ADDRESS_TCP_RX;
//   	tcp_rx_address.sin_port = htons(SOCKET_PORT_TCP_RX );
//
//   	if(bind(sock_tcp_rx, (struct sockaddr *)&tcp_rx_address, sizeof(tcp_rx_address)) < 0)
//   	{
//   		ESP_LOGI(TAG_SOCKET, "Error bind connection");
//   	    close(sock_tcp_rx);
//   	}
//   	listen(sock_tcp_rx, 3);
//   	ESP_LOGI(TAG_SOCKET,"rx ready");
//   	xTaskCreate(&socket_tcp_rx, "socket_tcp_rx", 1024, NULL, 5, NULL);
//}
//
///* SOCKET TO RECEIVE A COMMAND OVER TCP*/
//IRAM_ATTR void socket_tcp_rx(void *ignore){
//	xQueue_to_camera_tcp = xQueueCreate(QUEUE_BUFFER_SIZE, QUEUE_TO_SERVER_MQTT_LENGTH);
//	int recv_data;
//	memset(socket_data_to_camera, 0, strlen(socket_data_to_camera));
//   	longs = sizeof(server_address);
//   	int server;
//   	const TickType_t xBlockTime = pdMS_TO_TICKS(10);
//   	while(1){
//   		server = accept(sock_tcp_rx, (struct sockaddr *)&server_address, &longs);
//   		if(server < 0) {
//   			close(sock_tcp_rx);
//   		}
//
//   		recv_data = recv(server, socket_data_to_camera, sizeof(socket_data_to_camera), 0);
//   		if(recv_data > 0){
//   			xQueueSend(xQueue_to_camera_tcp, &socket_data_to_camera, xBlockTime);
//   			spi_wakeup_high();
//   			memset(socket_data_to_camera, 0, strlen(socket_data_to_camera));
//   		}
//   		close(server);
//   	}
//}

/* SOCKET UDP SEND CONFIGURATION */
void socket_udp_cfg(void){
	while(false == connected){
		vTaskDelay(2000 / portTICK_RATE_MS);
	}
	sock_udp_tx = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (sock_udp_tx < 0) {
		ESP_LOGI(TAG_SOCKET, "CREATE SOCKET STATUS: %s", strerror(errno));
		close(sock_udp_tx);
	}

	udp_tx_address.sin_family = AF_INET;
	inet_pton(AF_INET, SERVER_ADDRESS, &udp_tx_address.sin_addr.s_addr);
	udp_tx_address.sin_port = htons(SOCKET_PORT_UDP_TX);

	ESP_LOGI(TAG_SOCKET, "Socket UDP Ready");

	xTaskCreate(&socket_udp_send, "socket_udp_send", 1024, NULL, 3, NULL);
}

/* SOCKET TO SEND MULTIMEDIA OVER UDP*/
IRAM_ATTR void socket_udp_send(void *void_parameter){
	const TickType_t xBlockTime = pdMS_TO_TICKS( 10 );
	char end_queue_tx[3] = "EOT";
	while (1) {
		if (xQueue_to_server_udp!=0){
			if(xQueueReceive(xQueue_to_server_udp, &socket_data_to_server_udp, xBlockTime)==pdTRUE){
				if (strcmp(socket_data_to_server_udp, end_queue_tx) == 0){
					sendto(sock_udp_tx, end_queue_tx, sizeof(end_queue_tx), 0, (struct sockaddr *)&udp_tx_address, sizeof(udp_tx_address));
					ESP_LOGI(TAG_SOCKET, "End");
					vTaskDelay(xBlockTime);
				}
				else{
					sendto(sock_udp_tx, socket_data_to_server_udp, sizeof(socket_data_to_server_udp), 0, (struct sockaddr *)&udp_tx_address, sizeof(udp_tx_address));
				}
			}
		}
	}
}

