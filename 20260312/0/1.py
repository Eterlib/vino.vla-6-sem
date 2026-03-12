from pathlib import Path
import cmd


class cmdl(cmd.Cmd):
    prompt = ">=> "

    def do_EOF(self, args):
        return 1

    def emptyline(self):
        return

    def do_size(self, args):
        """print stat.st_size of file in arg"""
        p = Path(args)
        print(f"{p.name}: {p.stat().st_size}")

    def complete_size(self, text, line, begidx, endidx):
        parent_dir = Path(text).parent
        return [p.name for p in parent_dir.glob(f"{text.split('/')[-1]}*")]


if __name__ == "__main__":
    cmdl().cmdloop()
