server {
    listen [::]:80 default_server;
    server_name nott.tk;
    root /var/www/notes/project/;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:///run/uwsgi/app/notes/socket;
    }

    location /static/ {
        try_files $uri $uri/ =404;
    }
}