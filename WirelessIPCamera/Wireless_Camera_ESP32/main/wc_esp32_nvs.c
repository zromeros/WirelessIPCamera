/*
 * wc_esp32_nvs.c
 *
 *  Created on: 20 sept. 2018
 *      Author: Diego Perez
 *      email: diegoperez1295@gmail.com
 */
#define ESP_OK 0
#include "wc_esp32_nvs.h"

/* NVS CONFIGURATION */
void nvs_cfg(void){															//La configuracion de la NVS no retorna nada
    esp_err_t ret = nvs_flash_init(); 										//Se inicia la memoria, esta variable devuelve un valor que pude indicar un error
	if (ret == ESP_ERR_NVS_NO_FREE_PAGES) {									//En caso de que la memoria esté llena
		ESP_ERROR_CHECK(nvs_flash_erase());									//Se elimina lo que contenga la memoria flash y se verifica si hay error
		ret = nvs_flash_init();												//Se vuelve a iniciar la memoria
		ESP_LOGI(TAG_NVS,"LISTO\n");

	}
	ESP_ERROR_CHECK(ret);													//Se verifica que no haya errores al inicio
	ESP_LOGI(TAG_NVS, "NVS ready"); 											//Se coloca una etiqueta para indicar que la NVS está lista
	ESP_ERROR_CHECK(nvs_open("storage", NVS_READWRITE, &my_handle));		//Se chequean los errores y se abre la NVS
																			//La apertura recibe un string con el nombre, el modo de apertura (que es leer-escribir)
																			//y la direccion de un handler del tipo nvs_handler declarado en el header
}

/* READ A VALUE OF NVS */
char * nvs_read(char* key){													//Funcion para leer lo que hay en la NVS
	size_t required_size;													//Tamaño requerido del tipo unsigned int para esta variable
	nvs_get_str(my_handle, key, NULL, &required_size);						//Se toma lo que haya en memoria como un string, recibe como parámetros el handler usado anteriormente
																			//el valor reibido por referencia del tipo char, valor de salida y lengh
	char* value = malloc(required_size);									//Se reserva un espacio de memoria que se va a pasar por referencia a la funcion nvs_get_str
	esp_err_t err = nvs_get_str(my_handle, key, value, &required_size);		//Verificacion de errores

	switch (err) {
		case ESP_OK:					//ESP_OK									//En caso de que en err se reciba ESP_OK, se etiqueta el key y el valor del espacio de memoria asignado
			ESP_LOGI(TAG_NVS,"key: %s Value: %s", key, value);
			return value;													//Se retorna valor del espacio de memoria asignado
			break;
		case ESP_ERR_NVS_NOT_FOUND:											//En caso de que no se encuentre la NVS, se etiqueta que no se ha podido inicializar un valor todavía
			ESP_LOGI(TAG_NVS,"The value is not initialized yet!\n");
			return NVS_READ_ERROR;											//Se retona un error de lectura
			break;
		default :
			ESP_LOGI(TAG_NVS,"Error (%s) reading!\n", esp_err_to_name(err));
			return NVS_READ_ERROR;											//En vaso de cualquier otro error, se retorna error de lectura
	}
}


//Funcion para limpiar credenciales cuando se alamacenan de manera incorrecta.
void nvs_clear_credentials(void){
	nvs_erase_key(my_handle, "ssid");										//Se elimina lo que esté ubicado en en ssid
	nvs_erase_key(my_handle, "password");									//Se elimina lo que esté ubicado en password
	ESP_LOGI(TAG_NVS,"Credentials cleared\n"); 								//Se etiqueta para indicar que las credenciales se eliminaron
	nvs_commit(my_handle);													//se actualiza el handler
}
