sudo nvidia-xconfig --preserve-busid -a --virtual=1280x1024
sudo Xorg :0 &
sleep 1
./bin/LinetraceWorld/LinetraceWorld.sh -env=/tmp/simulator_env.json -RenderOffscreen
