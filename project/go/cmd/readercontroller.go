/*
Copyright © 2025 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"go-root/readercontroller"

	"github.com/spf13/cobra"
)

// readercontrollerCmd represents the readercontroller command
var readercontrollerCmd = &cobra.Command{
	Use:   "readercontroller",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: readercontroller.Cmd,
}

func init() {
	rootCmd.AddCommand(readercontrollerCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// readercontrollerCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// readercontrollerCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
