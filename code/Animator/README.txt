Init docker with
	sudo docker run -P lowerquality/gentle 

Find docker processes (and their GENTLE_DOCKER_PORT)
	sudo docker ps

Curl requests like
	curl -F "audio=@you-can-do-it.wav" -F "transcript=@you-can-do-it.txt" "0.0.0.0:{GENTLE_DOCKER_PORT}/transcriptions?async=false"
