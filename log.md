# 开发过程中遇到的问题及其解决方法

## 数据库部分
1.Mysql 更改字符集
- 先切换到需要转换的数据库：use data_dev;
- 然后查看当前数据库的编码：show variables like 'character_set_database'; 
- 然后把它的编码转成utf8：alter database data_dev CHARACTER SET utf8;

2.数据库命令
- 初始化数据库：python manage.py db init
- 数据库迁移：python manage.py db migrate -m " nth migration"
- 更新数据库：python manage.py db upgrade
