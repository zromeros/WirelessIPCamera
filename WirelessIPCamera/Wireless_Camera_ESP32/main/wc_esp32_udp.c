#include "wc_esp32_udp.h"

DRAM_ATTR char socket_data_to_server_udp[QUEUE_TO_SERVER_UDP_LENGTH]="";
/* SOCKET UDP SEND CONFIGURATION */
void socket_udp_cfg(void){
	//Delay para esperar conexion a internet
	while(false == connected){
		vTaskDelay(2000 / portTICK_RATE_MS);
	}

	// CORREGIR: Generar el socket obligatoriamente (while)
	sock_udp_tx = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP); //Esto devuelve un número que dice que a qué referencia está conectado
					//socket(Dominio,tipo,protocolo)
	if (sock_udp_tx < 0) { //En caso de que el entero sea negativo, no se genera el socket correctamente
		ESP_LOGI(TAG_SOCKET, "CREATE SOCKET STATUS: %s", strerror(errno));
		close(sock_udp_tx);
	}
	// wrap

	udp_tx_address.sin_family = AF_INET; //Se indica la familia
	inet_pton(AF_INET, SERVER_ADDRESS, &udp_tx_address.sin_addr.s_addr); //Se le da direccion
	udp_tx_address.sin_port = htons(SOCKET_PORT_UDP_TX);//Se agrega el puerto de transmision

	ESP_LOGI(TAG_SOCKET, "Socket UDP Ready");

	// Iniciar tarea para controlar el envio por socket UDP
	//xTaskCreate(&socket_udp_send, "socket_udp_send", 1024, NULL, 3, NULL); //descomentar
	xTaskCreate(&socket_udp_send, "socket_udp_send", QUEUE_TO_SERVER_UDP_LENGTH, NULL, 3, NULL);
	//xTaskCreatePinnedToCore( &socket_udp_send, "socket_udp_send", QUEUE_TO_SERVER_UDP_LENGTH, NULL, 3, NULL, 2 );
}

/* SOCKET TO SEND MULTIMEDIA OVER UDP*/
IRAM_ATTR void socket_udp_send(void *void_parameter){
	const TickType_t xBlockTime = pdMS_TO_TICKS(10);
	char end_queue_tx[4] = "EOT";
	char end_frames_tx[4] = "END";
	//char inicio[3] = "\xff\xd8\x00";
	//char final[3] = "\xff\xd9\t";
	while (1) {
		if (xQueue_to_server_udp!=0){
			if(xQueueReceive(xQueue_to_server_udp, &socket_data_to_server_udp, xBlockTime)==pdTRUE){
				/*En caso de que se envíe el final de una imagen, se envía 'EOT' al servidor*/
				if (strcmp(socket_data_to_server_udp, end_queue_tx) == 0){
					sendto(sock_udp_tx, end_queue_tx, 3, 0, (struct sockaddr *)&udp_tx_address, sizeof(udp_tx_address));
					vTaskDelay(xBlockTime);
					//c = 1;
				}
				/*En caso de que se envíe el final de varios frames, se envia 'END' por UDP*/
				else if (strcmp(socket_data_to_server_udp, end_frames_tx) == 0){
					sendto(sock_udp_tx, end_frames_tx, 3, 0, (struct sockaddr *)&udp_tx_address, sizeof(udp_tx_address));
					vTaskDelay(xBlockTime);

				}
				/*Se envía la trama completa recibida por SPI*/
				else{

					sendto(sock_udp_tx, socket_data_to_server_udp, sizeof(socket_data_to_server_udp), 0, (struct sockaddr *)&udp_tx_address, sizeof(udp_tx_address));
					vTaskDelay(xBlockTime);
				}
			}
		}
	}
}
