
import sys
import time

plog_field_count = 7
plog_size = 0
plog_next_idx = 0
plog = None


def alloc_plog(size):
	global plog_size, plog
	plog_size = size
	plog = [[None]*plog_field_count for x in range(size)]


def analize_plog(plog):
	frame_stats = {}
	func_stats = {}
	for op, frame_id, parent_frame_id, filename, lineno, func_name, now_us in plog:
		loc_id = (filename, lineno, func_name)
		# print(op, arg, id(frame), loc_id)
		if op == 'call':
			frame_stats[frame_id] = [now_us, 0]
		elif op == 'return' or op == 'exception':
			start_tm_us, callees_acc_us = frame_stats[frame_id]
			duration_us = now_us - start_tm_us
			# add total time spent in this frame to the parent frame
			if parent_frame_id in frame_stats:
				frame_stats[parent_frame_id][1] += duration_us
			# subtract time spent in callees from current frame
			duration_us -= callees_acc_us

			#print(op, arg, frame_id, loc_id, 'parent frame:\t', parent_frame_id, 'acc:\t', callees_acc_us, frame_stats[parent_frame_id][1] if parent_frame_id in frame_stats else 0, duration_us)
			del frame_stats[frame_id]
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
	return func_stats


def _log_trace_func(frame, op, arg):
	global plog_next_idx
	if op == 'line':
		return
	now_us = time.ticks_us()
	if plog_next_idx >= plog_size:
		return
	code = frame.f_code
	# assigning like this `[index][:] = fields` does not replace the item in the outer list
	plog[plog_next_idx][:] = op, id(frame), id(frame.f_back), code.co_filename, frame.f_lineno, code.co_name, now_us
	plog_next_idx += 1
	return _log_trace_func


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

alloc_plog(1000)

sys.settrace(_log_trace_func)

__main__()
print(analize_plog(plog))
