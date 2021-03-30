# Blog

## 2021-03-30
After performing some tests using the CrazyFrog endpoint and client
(see [CrazyFrog](../tests/crazyfrog)) located in the test folder I saw that
actively waiting until the message got published is not working well. It is
decreasing throughput performance. Polling the `is_published()` method on the message
being sent is not a good idea. 

I am going to change the code and work with the `on_publish()` callback to check if the
message was sent successfully.
