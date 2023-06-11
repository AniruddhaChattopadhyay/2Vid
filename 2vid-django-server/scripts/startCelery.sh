source ~/miniconda3/etc/profile.d/conda.sh
conda activate newsx-django
sudo service rabbitmq-server start
sudo service rabbitmq-server status
celery -A newsX_backend worker --loglevel=INFO
