docker run \
		-v ~/CNN-WordSim/params:/main_dir/params \
		-v /storage/data_don:/main_dir/data \
		-it \
		--shm-size 8G \
		--rm \
		don_vgg:0.1