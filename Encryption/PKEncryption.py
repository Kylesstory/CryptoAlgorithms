from Essential import Utilities as utils
import abc

class PKEncryption(object):
	"""docstring for PKEncryption"""
	def __init__(self, arg):
		raise NotImplementedError("PKEncryption is abstract.")
	
	@abc.abstractmethod
	def encrypt(self,m):
		pass
	
	@abc.abstractmethod
	def decrypt(self, c):
		pass

class RSA(PKEncryption):
	"""docstring for RSA"""
	def __init__(self, security):
		self.security = security
		self.n, p2q2 = utils.composeOrder(security)
		_lambda = p2q2 << 1
		self.e = utils.coPrime(security, _lambda)
		self.d = utils.modinv(self.e, _lambda)

	def encrypt(self, m):
		return pow(m, self.e, self.n)

	def decrypt(self, c):
		return pow(c, self.d, self.n)

	def homomorphic(self, c1, c2):
		return (c1 * c2) % self.n

	def demo(self, message):
		c = self.encrypt(message)
		param = {'security': self.security, 'n': self.n, 'd': self.d, 'e': self.e, 'message': message, 'encrypted': c, 'decrypted': self.decrypt(c)}
		utils.colorfulPrint('RSA encryption', param)

class ElGamal(PKEncryption):
	"""docstring for ElGamal"""
	def __init__(self, security):
		self.security = security
		self.p, self.q, self.g = utils.primeOrder(security)
		self.x, self.y = utils.dlPair(security, self.g, self.q, self.p)

	def encrypt(self, m):
		r, c1 = utils.dlPair(self.security, self.g, self.q, self.p)
		c2 = (m * pow(self.y, r, self.p)) % self.p
		return [c1, c2]

	def decrypt(self, c):
		return c[1] * utils.modinv(pow(c[0], self.x, self.p), self.p) % self.p

	def homomorphic(self, pk, c1, c2):
		return [(c1[0] * c2[0]) % self.p, (c1[1] * c2[1]) % self.p]

	def demo(self, message):
		c = self.encrypt(message)
		param = {'security': self.security, 'g': self.g, 'q': self.q, 'p': self.p, 'sk': self.x, 'pk': self.y, 'message': message, 'encrypted': c, 'decrypted': self.decrypt(c)}
		utils.colorfulPrint('ElGamal encryption', param)

class Paillier(PKEncryption):
	"""docstring for Paillier"""
	def __init__(self, security):
		self.security = security
		self.n, self.sk = utils.composeOrder(security)
		self.n2 = self.n * self.n
		x = utils.randomBits(2 * security) % self.n2
		self.g = pow(x, 2, self.n2)

	def encrypt(self, m):
		r = utils.coPrime(2 * self.security, self.n2, self.sk * self.n)
		rn = pow(r, self.n, self.n2)
		return (pow(self.g, m, self.n2) * rn) % self.n2

	def decrypt(self, c):
		x = self.L(pow(c, self.sk, self.n2))
		y = self.L(pow(self.g, self.sk, self.n2))
		return (x * utils.modinv(y, self.n)) % self.n

	def homomorphic(self, c1, c2):
		return (c1 * c2) % self.n2

	def L(self, x):
		return int((x - 1) % self.n2 / self.n)

	def demo(self, message):
		c = self.encrypt(message)
		param = {'security': self.security, 'n2': self.n2, 'n': self.n, 'sk': self.sk, 'g': self.g, 'message': message, 'encrypted': c, 'decrypted': self.decrypt(c)}
		utils.colorfulPrint('Paillier encryption', param)

class CramerShoup(PKEncryption):
	"""docstring for CramerShoup"""
	def __init__(self, security):
		self.security = security
		self.p, self.q, self.g = utils.primeOrder(security)
		self.h = self.g
		while self.h == self.g:
			self.h = utils.coPrime(security, self.p, self.q)
		self.sk = [utils.randomBits(security - 1) % self.q for i in range(5)]
		self.c = pow(self.g, self.sk[0], self.p) * pow(self.h, self.sk[1], self.p) % self.p
		self.d = pow(self.g, self.sk[2], self.p) * pow(self.h, self.sk[3], self.p) % self.p
		self.y = pow(self.g, self.sk[4], self.p)

	def encrypt(self, m):
		r = utils.randomBits(self.security) % self.q 
		u = pow(self.g, r, self.p)
		v = pow(self.h, r, self.p)
		w = m * pow(self.y, r, self.p) % self.p
		h = utils.hash([u, v, w], self.security - 1)
		t = (self.c * pow(self.d, h, self.p)) % self.p
		x = pow(t, r, self.p)
		return [u, v, w, x]

	def decrypt(self, c):
		h = utils.hash([c[0], c[1], c[2]], self.security - 1)
		t = (pow(c[0], ((self.sk[0] + self.sk[2] * h) % self.q) , self.p) * pow(c[1], ((self.sk[1] + self.sk[3] * h) % self.q), self.p)) % self.p
		if c[3] == t:
			m = (c[2] * utils.modinv(pow(c[0], self.sk[4], self.p), self.p)) % self.p
			return m
		else:
			print(c[3])
			print(t)
			return 0

	def demo(self, message):
		pks = [self.c, self.d, self.y]
		c = self.encrypt(message)
		param = {'security': self.security, 'g': self.g, 'h': self.h, 'q': self.q, 'p': self.p, 'sk': self.sk, 'pk': pks, 'message': message, 'encrypted': c, 'decrypted': self.decrypt(c)}
		utils.colorfulPrint('Cramer Shoup encryption', param)