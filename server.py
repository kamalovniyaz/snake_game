import socket

res = []


def step(u1, u2):
    u1.send("Твой ход".encode("utf8"))
    u2.send("Ход противника".encode("utf8"))
    answer = u1.recv(32)
    res.append(answer.decode("utf8"))
    u2.send(answer)

    return res


sock = socket.socket()
port = 50008
sock.bind(("localhost", port))
sock.listen(2)
user1, addr1 = sock.accept()
user2, addr2 = sock.accept()

while True:
    step(user1, user2)
    user1, user2 = user2, user1
