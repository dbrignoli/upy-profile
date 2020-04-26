
import sys
import time

frame_stats = {}
func_stats = {}

def _trace_func(frame, op, arg):
	now_us = time.ticks_us()
	# print(dir(frame))
	# print(frame.f_back, frame.f_code, frame.f_lasti, frame.f_lineno, frame.f_globals)
	# print(dir(code))
	# print(code.co_code, code.co_consts, code.co_filename, code.co_firstlineno, code.co_lnotab, code.co_name, code.co_names)

	code = frame.f_code
	loc_id = (code.co_filename, frame.f_lineno, code.co_name)
	# print(op, arg, id(frame), loc_id)
	if op == 'call':
		frame_stats[id(frame)] = [now_us, 0]
	elif op == 'return' or op == 'exception':
		start_tm_us, callees_acc_us = frame_stats[id(frame)]
		duration_us = now_us - start_tm_us

		# add total time spent in this frame to the parent frame
		parent_frame_id = id(frame.f_back)
		if parent_frame_id in frame_stats:
			frame_stats[parent_frame_id][1] += duration_us
		# subtract time spent in callees from current frame
		duration_us -= callees_acc_us

		#print(op, arg, id(frame), loc_id, 'parent frame:\t', parent_frame_id, 'acc:\t', callees_acc_us, frame_stats[parent_frame_id][1] if parent_frame_id in frame_stats else 0, duration_us)
		del frame_stats[id(frame)]
		code = frame.f_code
		loc_id = (code.co_filename, frame.f_lineno, code.co_name)
		if loc_id in func_stats:
			call_count, min_us, max_us, tot_us = func_stats[loc_id]
			call_count += 1
			min_us = min(min_us, duration_us)
			max_us = max(max_us, duration_us)
			tot_us += duration_us
		else:
			call_count, min_us, max_us, tot_us = (1, duration_us, duration_us, duration_us)
		func_stats[loc_id] = call_count, min_us, max_us, tot_us
	else:
		pass
	return _trace_func

def test2(a):
	#time.sleep(0.1)
	pass


def test1(a):
	test2(a)
	test2(a)
	test2(a)
	test2(a)
	test2(a)


def __main__():
	test1('lalala')
	test1('qaqaqa')

sys.settrace(_trace_func)

__main__()
print(func_stats)
