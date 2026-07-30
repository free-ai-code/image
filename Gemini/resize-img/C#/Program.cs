using System;
using System.IO;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length < 4)
        {
            Console.WriteLine("使い方: dotnet run <入力画像> <出力画像> <幅> <高さ>");
            Console.WriteLine("例:     dotnet run input.jpg output.jpg 800 600");
            return;
        }

        string inputPath = args[0];
        string outputPath = args[1];

        if (!int.TryParse(args[2], out int width) || !int.TryParse(args[3], out int height))
        {
            Console.WriteLine("エラー: 幅と高さには正の数値を指定してください。");
            return;
        }

        if (!File.Exists(inputPath))
        {
            Console.WriteLine($"エラー: ファイルが見つかりません -> {inputPath}");
            return;
        }

        try
        {
            // 画像の読み込みとリサイズ
            using (Image image = Image.Load(inputPath))
            {
                image.Mutate(x => x.Resize(width, height));
                image.Save(outputPath);
            }

            Console.WriteLine($"成功: リサイズ画像を保存しました -> {outputPath} ({width}x{height})");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"エラーが発生しました: {ex.Message}");
        }
    }
}
