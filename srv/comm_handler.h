
#ifndef SRV_COMM_HANDLER_H
#define SRV_COMM_HANDLER_H

void unpack_pos_data(char *buf);
void unpack_motctrl_data(char *buf);
void unpack_sdo_upload(char *buf);

#endif //SRV_COMM_HANDLER_H
