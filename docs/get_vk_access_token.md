Get VK token
============

### [Implicit Flow](https://vk.com/dev/implicit_flow_user)

Этот метод дожен использовать либо на JavaScript, либо на мобильных приложениях. 

> Используйте Implicit Flow для вызова методов API ВКонтакте непосредственно с устройства 
> пользователя (например, из Javascript). 
> Ключ доступа, полученный таким способом, не может быть использован для запросов с сервера.

- [Get token for user](https://oauth.vk.com/authorize?client_id=5344865&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,offline&response_type=token&v=5.69&state=123456)

### [Authorization Code Flow](https://vk.com/dev/authcode_flow_user)

> Используйте Authorization Code Flow для вызова методов API ВКонтакте с серверной части 
> Вашего приложения (например, из PHP). 
> Ключ доступа, полученный таким способом, не привязан к IP-адресу, но набор прав, которые может 
> получить приложение, ограничен из соображений безопасности.

- [Get code for user](https://oauth.vk.com/authorize?client_id=5344865&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,offline&response_type=code&v=5.69&state=123456)

### [Auth for groups](https://vk.com/dev/access_token?f=2.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0)

- [Get code for group](https://oauth.vk.com/authorize?client_id=5344865&display=page&redirect_uri=https://oauth.vk.com/blank.html&group_ids=88923650&scope=messages&response_type=code&v=5.69)
- [Get token for group](https://oauth.vk.com/access_token?client_id=5344865&client_secret=*&redirect_uri=https://oauth.vk.com/blank.html&code=*)
