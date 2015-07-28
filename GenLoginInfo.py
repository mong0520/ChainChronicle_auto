import re
import sys

class GenLoginInfo():

    def getUid(self, loginString):
        m = re.search('UniqueID%2522%253a%2522(.+?)%2522%252c%2522Sys', loginString)
        if m:
            found = m.group(1)
            return found
        else:
            return None
    
    def getToken(self, loginString):
        m = re.search('Token%2522%253a%2522(.+?)%2522', loginString)
        if m:
            found = m.group(1)
            return found
        else:
            return None
    

if __name__ == "__main__":
    #loginString = "cnt={0}&nature=cnt%3d{0}%26param%3d%257b%2522APP%2522%253a%257b%2522Version%2522%253a%25222.22%2522%252c%2522time%2522%253a%25221436052183%2522%252c%2522Lang%2522%253a%2522Chinese%2522%257d%252c%2522DEV%2522%253a%257b%2522Model%2522%253a%2522Xiaomi%2bMI%2b3W%2522%252c%2522CPU%2522%253a%2522ARMv7%2bVFPv3%2bNEON%2522%252c%2522GPU%2522%253a%2522Adreno%2b(TM)%2b330%2522%252c%2522OSVersion%2522%253a%2522Android%2bOS%2b4.4.4%2b%252f%2bAPI-19%2b(KTU84P%252fV6.5.3.0.KXDMICD)%2522%252c%2522UserUniqueID%2522%253a%2522ANDO4779bf78-f0f7-4a16-8d41-3c0d9ab46e0c%2522%252c%2522SysRAM%2522%253a1850%252c%2522VideoRAM%2522%253a198%252c%2522OS%2522%253a%25222%2522%252c%2522Token%2522%253a%2522APA91bEAKkkmD_eJ07r_NjRMRKJ2keH1A1Ju8mC2MDd9Iu9Bogxoy-HBl8SlCJJmMEM-aCMxnMEDNr-AC5TIiKmUHGRkk-lO1ypSdZhE8PhlQLjvBub3t81kwwwxIDQPw6CsarSI_BJ8%2522%257d%257d&param=%7b%22APP%22%3a%7b%22Version%22%3a%222.22%22%2c%22time%22%3a%221436052183%22%2c%22Lang%22%3a%22Chinese%22%7d%2c%22DEV%22%3a%7b%22Model%22%3a%22Xiaomi+MI+3W%22%2c%22CPU%22%3a%22ARMv7+VFPv3+NEON%22%2c%22GPU%22%3a%22Adreno+(TM)+330%22%2c%22OSVersion%22%3a%22Android+OS+4.4.4+%2f+API-19+(KTU84P%2fV6.5.3.0.KXDMICD)%22%2c%22UserUniqueID%22%3a%22{2}%22%2c%22SysRAM%22%3a1850%2c%22VideoRAM%22%3a198%2c%22OS%22%3a%222%22%2c%22Token%22%3a%22{3}%22%7d%7d&timestamp={1}"    
    print "[Login]"
    loginString = sys.argv[1]

    u = GenLoginInfo()
    uid = u.getUid(loginString)
    print "Uid = {0}".format(uid)

    token = u.getToken(loginString)
    print "Token = {0}".format(token)
