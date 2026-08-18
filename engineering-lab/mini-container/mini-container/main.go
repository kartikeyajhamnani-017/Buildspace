package main

import(
	"fmt"
	"os"
	"os/exec"
)

func main(){
	if(len(os.Args) < 3){
		fmt.Println("Usage: mini-container run <command> [args...]")
		os.Exit(1)
	}

	if os.Args[1] != "run" {
		fmt.Println("unknown command:", os.Args[1])
		os.Exit(1)
	}

	command := os.Args[2]
	args := os.Args[3:]

	cmd := exec.Command(command,args...)

	cmd.Stdin = os.Stdin 
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		
}