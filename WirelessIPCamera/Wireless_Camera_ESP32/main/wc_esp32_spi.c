/*
 * spi.c
 *
 *  	Created on: 10 ago. 2018
 *      	Author: Diego Perez
 *   Modificate by: Zadkiel Romero
 */
#include "wc_esp32_spi.h"
//#include "driver/uart.h"
#include "esp_heap_caps.h"

#define ECHO_TEST_TXD  (GPIO_NUM_4)
#define ECHO_TEST_RXD  (GPIO_NUM_5)
#define ECHO_TEST_RTS  (UART_PIN_NO_CHANGE)
#define ECHO_TEST_CTS  (UART_PIN_NO_CHANGE)

/*
const uart_config_t uart_config = {
        .baud_rate = 2000000,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
*/
volatile bool send_data = false;

// Transaction for SPI transmit
// DRAM_ATTR sirve para guardar en RAM en vez de Flash
DRAM_ATTR char spi_data_to_server[QUEUE_TO_SERVER_UDP_LENGTH]="";
DRAM_ATTR char spi_data_command[QUEUE_COMMAND_LENGTH]="";
DRAM_ATTR char spi_end[6]="FFFFFF"; //esta linea la agregue yo: Zadkiel
DRAM_ATTR char spi_tx_buffer[32]="";
DRAM_ATTR QueueHandle_t xQueue_to_server_udp = NULL;
DRAM_ATTR char spi_data_to_camera_tcp[QUEUE_TO_CAMERA_TCP_LENGTH]="";
DRAM_ATTR static const int RX_BUF_SIZE = 1024; //zadkiel
/*	SET HANDSHAKE LINE HIGH */
void my_post_setup_cb(spi_slave_transaction_t *trans) {
    WRITE_PERI_REG(GPIO_OUT_W1TS_REG, (1<<GPIO_SPI_HANDSHAKE));
}

/*	SET HANDSHAKE LINE LOW */
void my_post_trans_cb(spi_slave_transaction_t *trans) {
    WRITE_PERI_REG(GPIO_OUT_W1TC_REG, (1<<GPIO_SPI_HANDSHAKE));
}

/*	SET WAKEUP LINE HIGH */
void spi_wakeup_high(void) {
    WRITE_PERI_REG(GPIO_OUT_W1TS_REG, (1<<GPIO_SPI_WAKEUP));
}

/*	SET WAKEUP LINE LOW */
void spi_wakeup_low(void) {
    WRITE_PERI_REG(GPIO_OUT_W1TC_REG, (1<<GPIO_SPI_WAKEUP));
}

/* SPI PORT CONFIGURATION */
void spi_cfg(void){

    //Configuration for the SPI bus
    spi_bus_config_t buscfg = {
        .mosi_io_num = GPIO_SPI_MOSI,
        .miso_io_num = GPIO_SPI_MISO,
        .sclk_io_num = GPIO_SPI_SCLK
    };

    //Configuration for the SPI slave interface
    spi_slave_interface_config_t slvcfg = {
        .mode = SPI_MODE,
        .queue_size = SPI_QUEUE_SIZE,
        .flags = SPI_FLAGS,
		.spics_io_num = GPIO_SPI_CS,
		//callbacks para el handshake
		.post_setup_cb = my_post_setup_cb,
		.post_trans_cb = my_post_trans_cb
    };

    //Configuration for the handshake line
    gpio_config_t io_conf_handshake={
   		.intr_type=GPIO_INTR_DISABLE,
		.mode=GPIO_MODE_OUTPUT,
		.pin_bit_mask=(1<<GPIO_SPI_HANDSHAKE)
    };
    //Configure handshake line as output
    gpio_config(&io_conf_handshake);

    //Configuration for the wakeup line
    gpio_config_t io_conf_wakeup={
   		.intr_type=GPIO_INTR_DISABLE,
		.mode=GPIO_MODE_OUTPUT,
		.pin_bit_mask=(1<<GPIO_SPI_WAKEUP)
    };

    //Configure the wakeup line as output
    gpio_config(&io_conf_wakeup);
    spi_wakeup_low();

    //Enable pull-ups on SPI lines so we don't detect rogue pulses when no master is connected.
    gpio_set_pull_mode(GPIO_SPI_MOSI, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(GPIO_SPI_SCLK, GPIO_PULLUP_ONLY);
    gpio_set_pull_mode(GPIO_SPI_CS, GPIO_PULLUP_ONLY);

	//
    //PARA VER POR UART

    uart_param_config(UART_NUM_0, &uart_config);
    uart_set_pin(UART_NUM_0, ECHO_TEST_TXD, ECHO_TEST_RXD, ECHO_TEST_RTS, ECHO_TEST_CTS);
    uart_driver_install(UART_NUM_0, 256, 1900*2, 0, NULL, 0);

    //
/*
    //Initialize SPI slave interface
    ret = spi_slave_initialize(HSPI_HOST, &buscfg, &slvcfg, SPI_DMA_CHANNEL);
    ESP_LOGI(TAG_SPI, "SPI Ready");
    xTaskCreate(&spi_receive, "spi_receive", 2048 + 1024, NULL, 3, NULL);
*/

}
#define PCKSZ 1500U
char *fucking_buffer;

/* SPI TRANSACTION: SEND AND RECEIVE */
IRAM_ATTR void spi_receive(void *void_parameters){
	xQueue_to_server_udp = xQueueCreate(10, QUEUE_TO_SERVER_UDP_LENGTH); //Se crea una cola
	char tmp = 0;
	char tmpChar[4];
	int *id = spi_data_command;
	uint *tmpInt = (uint*)tmpChar;
	spi_slave_transaction_t tspi[2];
	int c = 0;

	fucking_buffer = heap_caps_malloc(PCKSZ*2, MALLOC_CAP_DMA);
	

	while (1){
			if((tmp++&1) == 0) {
				tspi[0] = spi_transaction(NULL, fucking_buffer, PCKSZ);
				xQueueSend(xQueue_to_server_udp, fucking_buffer, xBlockTime);
				/*
				uart_wait_tx_done(UART_NUM_0, portMAX_DELAY);
				*tmpInt = tspi[0].trans_len;
				//uart_write_bytes(UART_NUM_0, tmpChar, 4);
				uart_write_bytes(UART_NUM_0, fucking_buffer, tspi[0].trans_len >> 3); // este
				*/
			}else{
				tspi[1] = spi_transaction(NULL, fucking_buffer + PCKSZ, PCKSZ);
				xQueueSend(xQueue_to_server_udp, fucking_buffer+ PCKSZ, xBlockTime);
				/*
				uart_wait_tx_done(UART_NUM_0, portMAX_DELAY);
				*tmpInt = tspi[1].trans_len;
				//uart_write_bytes(UART_NUM_0, tmpChar, 4);
				uart_write_bytes(UART_NUM_0, fucking_buffer + PCKSZ, tspi[1].trans_len >> 3);
				*/
			}
		}
	/*
	while (1){

		memset(spi_data_command, 0, 32);
		spi_transaction(NULL, spi_data_command, 32);
		if (CAMERA_HEADER == spi_data_command[0]){						//Se veridica que el primer elemento del arreglo sea 35
			switch(spi_data_command[1]){								//Se analiza el segundo elemento del arreglo para verificar protocolo

				case CAMERA_WAKEUP:  									//Caso WakeUp 10

					memset(spi_tx_buffer, 0, 32);
					spi_tx_buffer[0] = ESP32_HEADER;					//35
					spi_tx_buffer[1] = ESP32_ACK;					//6
					spi_transaction(spi_tx_buffer, NULL, 32);		//Se envia ACK
					send_data = true;									//Variable que ayuda a verificar si se va a enviar algo (Solo para WakeUp)

					while(send_data == true){							//send_data true le dice al ESP que tiene permitido enviar datos al STM
						vTaskDelay(2000 / portTICK_RATE_MS);
					}
					break;

				case CAMERA_ESP32_STATUS:

					memset(&spi_tx_buffer, 0, 32);
					spi_tx_buffer[0] = ESP32_HEADER;
					spi_tx_buffer[1] = ESP32_ACK;
					spi_transaction(spi_tx_buffer, NULL, 32);

					if(connected){
						spi_tx_buffer[1] = ESP32_CONNECTED;
					}
					else{
						spi_tx_buffer[1] = ESP32_DISCONNECTED;
					}

					spi_transaction(spi_tx_buffer, NULL, 32);
					break;

				case CAMERA_TX_IMAGE:

					memset(spi_tx_buffer, 0, 32);
					spi_tx_buffer[0] = ESP32_HEADER;
					spi_tx_buffer[1] = ESP32_ACK;
					spi_transaction(spi_tx_buffer, NULL, 32);
					while(1){

						if((tmp++&1) == 0) {
							tspi[0] = spi_transaction(NULL, fucking_buffer, PCKSZ);
							if(tspi[0].trans_len/8 == 32){ //Se indica que una imagen ya terminó
								//sirve para copiar en buffer
								snprintf(spi_data_to_server, QUEUE_TO_SERVER_UDP_LENGTH, "EOT");
								xQueueSend(xQueue_to_server_udp, &spi_data_to_server, xBlockTime);
								spi_transaction(spi_tx_buffer, NULL, 32);  //Se envía ACK cuando culmina la transmisión de la imagen
								break;
							}else{
								xQueueSend(xQueue_to_server_udp, fucking_buffer, xBlockTime);
							}
						}else{
							tspi[1] = spi_transaction(NULL, fucking_buffer + PCKSZ, PCKSZ);
							if(tspi[0].trans_len/8 == 32){ //Se indica que una imagen ya terminó
								snprintf(spi_data_to_server, QUEUE_TO_SERVER_UDP_LENGTH, "EOT");
								xQueueSend(xQueue_to_server_udp, &spi_data_to_server, xBlockTime);//descomentar
								spi_transaction(spi_tx_buffer, NULL, 32);  //Se envía ACK cuando culmina la transmisión de la imagen
								break;
							}else{
								xQueueSend(xQueue_to_server_udp, fucking_buffer + PCKSZ, xBlockTime);
							}
						}
					}
					break;

				case CAMERA_TX_AUDIO:

					memset(spi_tx_buffer, 0, 32);
					spi_tx_buffer[0] = ESP32_HEADER;
					spi_tx_buffer[1] = ESP32_ACK;
					spi_transaction(spi_tx_buffer, NULL, 32);

					while(1){// poner timeout en el futuro con portDELAY

						if((tmp++&1) == 0) {
							tspi[0] = spi_transaction(NULL, fucking_buffer, PCKSZ);
							if(tspi[0].trans_len/8 == 32){ //Se indica que una imagen ya terminó
								//sirve para copiar en buffer
								snprintf(spi_data_to_server, QUEUE_TO_SERVER_UDP_LENGTH, "EOT");
								xQueueSend(xQueue_to_server_udp, &spi_data_to_server, xBlockTime);
								spi_transaction(spi_tx_buffer, NULL, 32);  //Se envía ACK cuando culmina la transmisión de la imagen
								break;
							}else{
								xQueueSend(xQueue_to_server_udp, fucking_buffer, xBlockTime);
							}
						}else{
							tspi[1] = spi_transaction(NULL, fucking_buffer + PCKSZ, PCKSZ);
							if(tspi[0].trans_len/8 == 32){ //Se indica que una imagen ya terminó
								snprintf(spi_data_to_server, QUEUE_TO_SERVER_UDP_LENGTH, "EOT");
								xQueueSend(xQueue_to_server_udp, &spi_data_to_server, xBlockTime);//descomentar
								spi_transaction(spi_tx_buffer, NULL, 32);  //Se envía ACK cuando culmina la transmisión de la imagen
								break;
							}else{
								xQueueSend(xQueue_to_server_udp, fucking_buffer + PCKSZ, xBlockTime);
							}
					}
					break;


				case CAMERA_TO_SERVER:
					/// IMPORTANTE 10/01/2019
					spi_data_command[0] = ESP32_HEADER;
					spi_data_command[1] = ESP32_ACK;
					spi_transaction(spi_data_command, NULL, 32);

					// Realizar rutina para publicar VIA MQTT
					break;

				case CAMERA_ID:
					spi_data_command[0] = ESP32_HEADER;
					spi_data_command[1] = ESP32_ACK;
					spi_transaction(spi_data_command, NULL, 32); 				//Se envia ACK
					spi_transaction(NULL, spi_data_command, 32); 				//Se recibe el ID de la camara
					sprintf(camera_id, "%08x%08x%08x", id[2], id[1], id[0]);	//Se copia en memoria

					mqtt_pub_id(camera_id);
					mqtt_sub_id(camera_id);

					spi_data_command[0] = ESP32_HEADER;
					spi_data_command[1] = ESP32_ACK;
					spi_transaction(spi_data_command, NULL, 32);				//Se envia ACK para culminar la transaccion

					break;

				case CAMERA_CONFIG:
					spi_data_command[0] = ESP32_HEADER;
					spi_data_command[1] = ESP32_ACK;
					spi_transaction(spi_data_command, NULL, 32);

					memset(&spi_data_to_server, 0, sizeof(spi_data_to_server));
					printf("algo\n");
					///AQUI SE ESTABLECE LA COMUNICACION CON EL SERVER
					spi_transaction(NULL,spi_data_to_server, 32);  //Se envía ACK cuando culmina la transmisión de la imagen
					xQueueSend(xQueue_to_server_udp, &spi_data_to_server, xBlockTime);
					//ZADKIEL
					break;
				default:
					break;
			}
		}

	}*/

}


void spi_q_transaction(char *tx, char *rx, int length, spi_slave_transaction_t *t){
	t->tx_buffer = tx;
	t->rx_buffer = rx;
	t->length = length*8; // conversion a bytes
	spi_slave_queue_trans(HSPI_HOST, t, portMAX_DELAY);
}


// Funcion para enviar y recibir a traves del SPI
spi_slave_transaction_t spi_transaction(char *tx, char *rx, int length){
	spi_slave_transaction_t t;
	memset(&t, 0, sizeof(t));
	t.tx_buffer = tx;
	t.rx_buffer = rx;
	t.length = length<<3; // conversion a bytes
	spi_slave_transmit(HSPI_HOST, &t, portMAX_DELAY);
	return t;
}

// Se llama desde otro sitio
void spi_to_camera(char *data_to_camera){

/* Se envia WakeUp y se recibe ACK. Eso tarda un instante de 10 ms */
	spi_wakeup_high();
    vTaskDelay(100 / portTICK_RATE_MS);
    spi_wakeup_low();
/****************************************************************/


	while(false == send_data){
		vTaskDelay(2000 / portTICK_RATE_MS);
	}
	sprintf(spi_data_command, "%s", data_to_camera);
	spi_transaction(spi_data_command, NULL, 32);
	ESP_LOGI(TAG_SPI, "Data Sent: %s", data_to_camera);
	send_data = false;
}

int spi_to_camera_id(char *data_to_camera){

/* Se envia WakeUp y se recibe ACK. Eso tarda un instante de 10 ms */
	spi_wakeup_high();
    vTaskDelay(100 / portTICK_RATE_MS);
    spi_wakeup_low();
/****************************************************************/
    int i = 0;
	while(false == send_data){
		vTaskDelay(2000 / portTICK_RATE_MS);
		i = i+1;
		if(i == 3){
			ESP_LOGI(TAG_SPI, "No WakeUp Answer to: %s", data_to_camera);
			return -1;
		}
	}
	sprintf(spi_data_command, "%s", data_to_camera);
	spi_transaction(spi_data_command, NULL, 32);
	ESP_LOGI(TAG_SPI, "Data Send: %s", data_to_camera);
	send_data = false;
	return 0;
}
