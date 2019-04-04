

with open('package.log', 'rb') as file:
	data = file.read()
	print('file size = {}'.format(len(data)))

idx0 = data.index(b'\xff\xd8\xff')
idx1 = data.index(b'\xff\xd9')

if idx1 < idx0:
	print("Limpiando imagen. idx = {}, {}".format(idx0, idx1))
	data = data[idx0:]

idx = 0
while True:
	try:
		idxb = data.index(b'\xff\xd8\xff')
		print("Image {}: idxb = {}".format(idx, idxb))
	except:	
		print("End of buffer: 0")
		break

	try:
		idxe = data.index(b'\xff\xd9')
		print("Image {}: idxe = {}".format(idx, idxe))
	except:	
		print("End of buffer: 1")
		break

	with open('prueba_video.avi', 'ab') as file:
		file.write(data[idxb:idxe+2])
	data = data[idxe+2:]
	idx = idx + 1