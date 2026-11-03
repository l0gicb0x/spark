from spark.core.channels import TextChannel


def test_text_channel_routes_input_and_output():
    delivered = []
    channel = TextChannel(lambda text: f"reply: {text}", delivered.append)
    reply = channel.receive("hello")
    channel.send(reply)
    assert reply == "reply: hello"
    assert delivered == ["reply: hello"]
