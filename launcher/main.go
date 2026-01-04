package main

import (
	"archive/zip"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"

	"golang.org/x/sys/windows"
)

func check(err error, message string) {
	if err != nil {
		fmt.Fprintf(os.Stderr, "❌ %s: %v\n", message, err)
		os.Exit(1)
	}
	fmt.Printf("✅ %s\n", message)
}

func downloadUV() error {
	filename := "uv.zip"

	// Проверяем, существует ли файл
	if _, err := os.Stat(filename); err == nil {
		fmt.Printf("✓ Файл %s уже существует, пропускаем скачивание\n", filename)
		return nil
	}

	// Используем магический URL GitHub для последнего релиза
	url := "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"

	fmt.Printf("Скачиваем %s...\n", filename)

	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("ошибка загрузки: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("неверный статус: %s", resp.Status)
	}

	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("не удалось создать файл: %w", err)
	}
	defer file.Close()

	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return fmt.Errorf("ошибка сохранения: %w", err)
	}

	fmt.Printf("✅ %s скачан\n", filename)
	return nil
}

func unzipUV() error {
	zipFile := "uv.zip"
	dir := "uv"
	targetExe := filepath.Join(dir, "uv.exe")

	if _, err := os.Stat(targetExe); err == nil {
		fmt.Printf("✓ Файл %s уже существует, пропускаем распаковку\n", targetExe)
		return nil
	}

	fmt.Printf("Распаковываем %s в папку %s...\n", zipFile, dir)

	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("не удалось создать папку %s: %w", dir, err)
	}

	r, err := zip.OpenReader(zipFile)
	if err != nil {
		return fmt.Errorf("не удалось открыть zip: %w", err)
	}
	defer r.Close()

	for _, f := range r.File {
		if f.Name != "uv.exe" {
			continue
		}

		rc, err := f.Open()
		if err != nil {
			return fmt.Errorf("ошибка открытия файла в архиве: %w", err)
		}

		out, err := os.Create(targetExe)
		if err != nil {
			rc.Close()
			return fmt.Errorf("не удалось создать %s: %w", targetExe, err)
		}

		_, err = io.Copy(out, rc)
		rc.Close()

		if err != nil {
			out.Close()
			return fmt.Errorf("ошибка копирования: %w", err)
		}

		if err := out.Close(); err != nil {
			return fmt.Errorf("ошибка закрытия файла: %w", err)
		}

		if err := os.Chmod(targetExe, 0755); err != nil {
			return fmt.Errorf("не удалось установить права: %w", err)
		}
	}

	fmt.Printf("✅ uv.exe распакован в папку %s\n", dir)
	return nil
}

// Скачивает репозиторий
func downloadPyv() error {
	filename := "pyv-master.zip"
	destDir := "pyv"
	url := "https://github.com/MrReDoX/pyv/archive/refs/heads/master.zip"

	// Если папка pyv уже существует - пропускаем скачивание
	if _, err := os.Stat(destDir); err == nil {
		fmt.Printf("✓ Папка %s уже существует, пропускаем скачивание\n", destDir)
		return nil
	}

	if _, err := os.Stat(filename); err == nil {
		fmt.Printf("✓ %s уже существует\n", filename)
		return nil
	}

	fmt.Printf("Скачиваем %s...\n", url)

	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("ошибка загрузки: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("неверный статус: %s", resp.Status)
	}

	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("не удалось создать файл: %w", err)
	}
	defer file.Close()

	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return fmt.Errorf("ошибка сохранения: %w", err)
	}

	return nil
}

// Распаковывает архив в директорию pyv
func unzipPyv() error {
	zipFile := "pyv-master.zip"
	destDir := "pyv"

	// Если папка уже существует - пропускаем распаковку
	if _, err := os.Stat(destDir); err == nil {
		fmt.Printf("✓ Папка %s уже существует, пропускаем распаковку\n", destDir)
		return nil
	}

	// Открываем архив
	r, err := zip.OpenReader(zipFile)
	if err != nil {
		return fmt.Errorf("не удалось открыть архив: %w", err)
	}
	defer r.Close()

	// Создаём целевую директорию
	os.MkdirAll(destDir, os.ModePerm)

	// Распаковываем все файлы
	for _, f := range r.File {
		// Убираем корневую папку из архива (pyv-master/)
		relPath := f.Name
		if len(relPath) > len("pyv-master/") && relPath[:11] == "pyv-master/" {
			relPath = relPath[11:] // Убираем "pyv-master/"
		}

		// Пропускаем пустые пути
		if relPath == "" {
			continue
		}

		// Полный путь для распаковки
		path := filepath.Join(destDir, relPath)

		// Если это директория
		if f.FileInfo().IsDir() {
			os.MkdirAll(path, os.ModePerm)
			continue
		}

		// Создаём директории для файла
		os.MkdirAll(filepath.Dir(path), os.ModePerm)

		// Открываем файл в архиве
		rc, err := f.Open()
		if err != nil {
			return fmt.Errorf("не удалось открыть файл в архиве: %w", err)
		}

		// Создаём файл на диске
		out, err := os.Create(path)
		if err != nil {
			rc.Close()
			return fmt.Errorf("не удалось создать файл: %w", err)
		}

		// Копируем содержимое
		_, err = io.Copy(out, rc)
		out.Close()
		rc.Close()

		if err != nil {
			return fmt.Errorf("ошибка копирования: %w", err)
		}
	}

	return nil
}

func runPyv() error {
	fmt.Println("🚀 Запускаем PyV...")

	// Копируем uv.exe только если его нет в pyv
	if _, err := os.Stat("pyv/uv.exe"); os.IsNotExist(err) {
		fmt.Println("📁 Копируем uv.exe в папку pyv...")
		data, err := os.ReadFile("uv/uv.exe")
		if err != nil {
			return err
		}
		if err := os.WriteFile("pyv/uv.exe", data, 0755); err != nil {
			return err
		}
		fmt.Println("✅ uv.exe скопирован")
	} else if err != nil {
		return err
	} else {
		fmt.Println("✓ uv.exe уже существует в папке pyv")
	}

	originalDir, _ := os.Getwd()
	defer os.Chdir(originalDir)
	os.Chdir("pyv")

	// Проверяем, установлены ли уже зависимости (есть ли venv папка)
	// В PyV зависимости обычно в .venv или venv
	venvExists := false
	if _, err := os.Stat(".venv"); err == nil {
		venvExists = true
	}
	if _, err := os.Stat("venv"); err == nil {
		venvExists = true
	}
	if _, err := os.Stat("pyproject.toml"); err != nil && !venvExists {
		// Если нет pyproject.toml и нет venv - что-то не так
		return fmt.Errorf("pyproject.toml не найден")
	}

	if !venvExists {
		fmt.Println("📦 Устанавливаем зависимости...")
		cmdSync := exec.Command(".\\uv.exe", "sync", "--active")
		cmdSync.Stdout = os.Stdout
		cmdSync.Stderr = os.Stderr
		if err := cmdSync.Run(); err != nil {
			return fmt.Errorf("ошибка uv sync: %w", err)
		}
	} else {
		fmt.Println("✓ Зависимости уже установлены")
	}

	fmt.Println("🎬 Запускаем PyV в фоне...")
	cmdRun := exec.Command(
		".\\uv.exe",
		"run",
		"--active",
		"pythonw",
		"src/Gui.py",
	)

	// Логи PyV в отдельный файл
	pyvLog, err := os.Create("pyv_log.txt")
	if err != nil {
		return err
	}
	defer pyvLog.Close()
	cmdRun.Stdout = pyvLog
	cmdRun.Stderr = pyvLog

	// Отвязка от консоли Windows
	cmdRun.SysProcAttr = &windows.SysProcAttr{
		CreationFlags: windows.DETACHED_PROCESS | windows.CREATE_NEW_PROCESS_GROUP,
		HideWindow:    true,
	}

	return cmdRun.Start() // запускаем и сразу выходим
}

func main() {
	// Сначала проверяем, есть ли уже все необходимое
	if _, err := os.Stat("uv/uv.exe"); err == nil {
		fmt.Println("✓ uv.exe уже установлен")
	} else {
		// Только если нет uv.exe - качаем
		check(downloadUV(), "скачивание uv")
		check(unzipUV(), "uv.exe распакован")
	}

	if _, err := os.Stat("pyv"); err == nil {
		fmt.Println("✓ pyv уже установлен")
	} else {
		// Только если нет папки pyv - качаем
		check(downloadPyv(), "репозиторий скачан")
		check(unzipPyv(), "репозиторий распакован")
	}

	// Проверяем, есть ли uv.exe в pyv
	if _, err := os.Stat("pyv/uv.exe"); os.IsNotExist(err) {
		fmt.Println("📁 Копируем uv.exe в папку pyv...")
		data, err := os.ReadFile("uv/uv.exe")
		check(err, "чтение uv.exe")
		check(os.WriteFile("pyv/uv.exe", data, 0755), "копирование uv.exe")
	}

	// Запускаем PyV
	if err := runPyv(); err != nil {
		fmt.Fprintf(os.Stderr, "❌ запуск pyv: %v\n", err)
		fmt.Println("Нажмите Enter для выхода...")
		fmt.Scanln()
		os.Exit(1)
	}
	os.Exit(0)
}
