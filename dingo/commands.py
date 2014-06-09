import newman

def main():
  """Entry point for command line access
  """
  cli = newman.Newman("Dingo - image resizing server", top_level_args={})

  import dingo.scripts.web

  cli.load_module(dingo.scripts.web, 'web')

  cli.go()
