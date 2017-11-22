def gen_commands(model_name_opts, s_batch_opts,
                 n_steps_opts, v_regularization_opts):
  for model_name in model_name_opts:
    for s_batch in s_batch_opts:
      for n_steps in n_steps_opts:
        for v_regularization in v_regularization_opts:
          yield "python3 -m NetDetect.src.main_iscx.train " \
                "--model_name=%s " \
                "--s_batch=%s " \
                "--n_steps=%s " \
                "--v_regularization=%s " \
                "--s_test=4096 " \
                "--s_report_interval=2400 " \
                "--s_save_interval=7200 " \
                % (model_name, s_batch, n_steps, v_regularization)


def main():
  model_name_opts = ["flowattmodel", "flowmodel"]
  s_batch_opts = [8, 32]
  n_steps_opts = [16, 28]
  v_regularization_opts = [0.01, 0.1, 0.4, 0.8, 1.2, 2]
  for command_ in gen_commands(model_name_opts, s_batch_opts,
                               n_steps_opts, v_regularization_opts):
    print(command_)


if __name__ == "__main__":
  main()
