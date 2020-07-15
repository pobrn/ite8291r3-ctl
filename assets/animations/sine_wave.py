import math
import time
from random import randint


def main():
	at = 0.0
	step = (2 * math.pi) / 16
	
	def f(x):
		return 2 + round( math.sin(x) * 3 )
	
	def rndcolor():
		return f"{randint(0,255)},{randint(0,255)},{randint(0,127)}"
	
	for i in range(16-1):
		
		v = f(at)
		at += step
		
		if not (0 <= v and v <= 5):
			continue
			
		print(f"pos {f(at)} {i} {rndcolor()}")
	
	
	while True:
		
		v = f(at)
		at += step
		
		if not (0 <= v and v <= 5):
			continue
		
		print(f"pos {v} 15 {rndcolor()}")
		print("apply", flush=True)
		
		time.sleep(0.1)
		
		print("shift 0 -1")
		
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
