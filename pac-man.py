if __name__ == "__main__":
    try:
        from src.pac_man.__main__ import main
        main()
    except ModuleNotFoundError as e:
        print(e, "\nMake sure you use 'make run'?")
