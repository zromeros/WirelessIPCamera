/*
 * socket.h
 *
 *  Created on: 14 ago. 2018
 *      Author: Diego Perez
 */
#ifndef SOCKET_H_
#define SOCKET_H_

/* INCLUDES */
#include "lwip/tcp.h"
#include <stdio.h>
#include <string.h>
#include <sys/fcntl.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_event_loop.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_log.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/netdb.h"
#include "lwip/dns.h"
#include "sdkconfig.h"
#include "wc_esp32_spi.h"
#include "wc_esp32_wifi.h"

/* DEFINES */

#define SERVER_ADDRESS		 	"192.168.0.94"
// TCP Sockets
#define SOCKET_PORT_TCP_TX 		4000
#define SOCKET_ADDRESS_TCP_RX	INADDR_ANY
#define SOCKET_PORT_TCP_RX 		4001
// UDP Sockets
#define SOCKET_PORT_UDP_TX	 	4003
// TAG
#define TAG_SOCKET "SOCKET"

/* GLOBAL VARIABLES */
//queue
extern QueueHandle_t xQueue_to_camera;
// Sockets
int sock_tcp_tx;
struct sockaddr_in tcp_tx_address;
int sock_tcp_rx;
struct sockaddr_in tcp_rx_address;
struct sockaddr_in server_address;
socklen_t longs;
int sock_udp_tx;
struct sockaddr_in udp_tx_address;


/* FUNCTIONS */
void socket_tcp_tx(char * data);
void socket_tcp_rx_cfg(void);
void IRAM_ATTR socket_tcp_rx(void *ignore);
void socket_udp_cfg(void);
void IRAM_ATTR socket_udp_send(void *void_parameter);

#endif /* SOCKET_H_ */
