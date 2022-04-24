from time import sleep
from des import encrypt, decrypt
from datetime import datetime


def now_int():
    return int(round(datetime.now().timestamp()))


def main():
    C = {
        "id": 2,
        "Kc": 2222,
        "ss_id": 3
    }
    AS = {
        "Kas_tgs": 2834123,
        "Kc": 2222,
        "Kc_tgs": 1234,
        "tgs_id": 2,
    }
    TGS = {
        "Kas_tgs": 2834123,
        "Ktgs_ss": 823,
        "Kc_ss": 81724,
        "ss_id": 3
    }
    SS = {
        "Ktgs_ss": 823,
        "Kc_ss": 81724
    }

    # step 1
    print(r"1. C -> AS: {c}")
    AS["client_id"] = C["id"]

    # step 2
    print(r"2. AS -> C: {{TGT}K(as_tgs), K(c_tgs)}K(c)")
    TGT = {
        "c": AS["client_id"], "tgs": AS["tgs_id"],
        "t1": now_int(), "p1": 300,
        "Kc_tgs": AS["Kc_tgs"]
    }
    for key in TGT:
        TGT[key] = encrypt(TGT[key], AS["Kas_tgs"])
        TGT[key] = encrypt(TGT[key], AS["Kc"])
    message_as_to_c = {"TGT_enc": TGT,
                       "Kc_tgs": encrypt(AS["Kc_tgs"], AS["Kc"])}

    # client received message
    C["TGT_as_tgs"] = message_as_to_c["TGT_enc"]
    for key in C["TGT_as_tgs"]:
        C["TGT_as_tgs"][key] = decrypt(C["TGT_as_tgs"][key], C["Kc"])
    C["Kc_tgs"] = decrypt(message_as_to_c["Kc_tgs"], C["Kc"])

    # step 3
    print(r"3. C -> TGS: {TGT}K(as_tgs), {Aut1}K(c_tgs), {ID}")
    aut1 = {
        "c": C["id"],
        "t2": now_int()
    }
    for key in aut1:
        aut1[key] = encrypt(aut1[key], C["Kc_tgs"])
    message_c_to_tgs = {
        "TGT_as_tgs": C["TGT_as_tgs"], "Aut1_c_tgs": aut1, "service_id": C["ss_id"]}

    # tgs received message
    TGS["TGT"] = message_c_to_tgs["TGT_as_tgs"]
    for key in TGS["TGT"]:
        TGS["TGT"][key] = decrypt(TGS["TGT"][key], TGS["Kas_tgs"])
    TGS["Aut1"] = message_c_to_tgs["Aut1_c_tgs"]
    for key in TGS["Aut1"]:
        TGS["Aut1"][key] = decrypt(TGS["Aut1"][key], TGS["TGT"]["Kc_tgs"])

    if TGS["Aut1"]["c"] != TGS["TGT"]["c"]:
        print("aut1 id != tgt id")
        return
    if TGS["Aut1"]["t2"] - TGS["TGT"]["t1"] > TGS["TGT"]["p1"]:
        print("tgt expired")
        return

    # step 4
    print(r"4. TGS -> C: {{TGS}K(tgs_ss), K(c_ss)}K(c_tgs)")
    _tgs = {
        "c": TGS["Aut1"]["c"],
        "ss": TGS["ss_id"],
        "t3": now_int(),
        "p2": 300,
        "Kc_ss": TGS["Kc_ss"]
    }
    for key in _tgs:
        _tgs[key] = encrypt(_tgs[key], TGS["Ktgs_ss"])
        _tgs[key] = encrypt(_tgs[key], TGS["TGT"]["Kc_tgs"])
    message_tgs_to_c = {
        "TGS_tgs_ss": _tgs,
        "Kc_ss": encrypt(TGS["Kc_ss"], TGS["TGT"]["Kc_tgs"])
    }

    # client received message
    C["TGS"] = message_tgs_to_c["TGS_tgs_ss"]
    for key in C["TGS"]:
        C["TGS"][key] = decrypt(C["TGS"][key], C["Kc_tgs"])
    C["Kc_ss"] = decrypt(message_tgs_to_c["Kc_ss"], C["Kc_tgs"])

    # step 5
    print(r"5. C -> SS: {TGS}K(tgs_ss), {Aut2}K(c_ss)")
    C["t"] = now_int()
    aut2 = {
        "c": C["id"],
        "t4": C["t"]
    }
    for key in aut2:
        aut2[key] = encrypt(aut2[key], C["Kc_ss"])
    message_c_to_ss = {
        "TGS": C["TGS"],
        "Aut2": aut2
    }

    # ss received message
    SS["TGS"] = message_c_to_ss["TGS"]
    for key in SS["TGS"]:
        SS["TGS"][key] = decrypt(SS["TGS"][key], SS["Ktgs_ss"])
    SS["Aut2"] = message_c_to_ss["Aut2"]
    for key in SS["Aut2"]:
        SS["Aut2"][key] = decrypt(SS["Aut2"][key], SS["Kc_ss"])

    if SS["TGS"]["c"] != SS["Aut2"]["c"]:
        print("aut2 id != tgs id")
        return
    if SS["Aut2"]["t4"] - SS["TGS"]["t3"] > SS["TGS"]["p2"]:
        print("tgs expired")
        return

    # step 6
    print(r"6. SS -> C: {t4+1}K(c_ss)")
    message_ss_to_c = {
        "t": encrypt(SS["Aut2"]["t4"] + 1, SS["Kc_ss"])
    }

    # client receved message
    time_from_message = decrypt(message_ss_to_c["t"], C["Kc_ss"])
    if time_from_message != C["t"] + 1:
        print(r"c[t] != ss[t]")
        return

    print("access granted")


if __name__ == "__main__":
    main()
