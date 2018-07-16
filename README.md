# check_nginx_upstream



##### 目的：
检测多个目录下NGINX配置文件中是否存在没有使用的upstream
##### 检测逻辑：

* 如果只存在一个upstream，不做深入检测

* 如果一个upstream全部被注释了，打印出{filename:[upstream_name]}

* 检测文件最后的location /下的proxy_pass 后面的为正在使用的upstream。将所有的upstream的名字和包含的IP找出来， 如果使用中的upstream的ip与其它的upstream中的IP不存在交集，说明这个
不在使用，打印出{filename:[upstream_name]}
##### 示例：
如下的文件，使用的为test_server_D，其与A，B组的IP都不存在交接，说明A,B两个组的IP都不在用，会打印出。

```
##test.test.com###
     upstream test_server_A {
        server 10.10.123.1:80 max_fails=1 fail_timeout=300s ;
        server 10.10.123.2:80 max_fails=1 fail_timeout=300s ;
     }

    upstream test_server_B {
        server 172.17.123.111:80 max_fails=1 fail_timeout=300s ;
     }
     upstream test_server_D {
        server 172.17.123.123:80 max_fails=1 fail_timeout=300s ;
     }
     server {
         listen 80;
         server_name     test.test.com;

         server_tokens   off;
         proxy_hide_header X-Powered-By;
         proxy_hide_header X-AspNet-Version;
         index default.htm index.html index.htm default.html;
         gzip on;

         include /etc/nginx/conf.d/errorpage.config;

         #access_log /file/test.com/*************.access.log  json;


         location / {
         proxy_pass        http://test_server_D;
         proxy_set_header        Host            $host;
         proxy_set_header        X-Real-IP       $remote_addr;
         proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
      }
}

```
