# web_pi_remote_gpio


* [Enable remote gpio](https://gpiozero.readthedocs.io/en/stable/remote_gpio.html)
    ```
    sudo raspi-config
    sudo pigpiod -n localhost -n $PUBLIC_IP
    ```

* Enable as daemon:
    ```
    sudo ln -s $PWD/web_pi_remote_gpio.service /etc/systemd/system/web_pi_remote_gpio.service
    sudo systemctl start web_pi_remote_gpio.service 
    ```
