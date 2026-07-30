#include <opencv2/opencv.hpp>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 5) {
        std::cout << "使い方: " << argv[0] << " <入力画像> <出力画像> <幅> <高さ>\n";
        return -1;
    }

    std::string inputPath = argv[1];
    std::string outputPath = argv[2];
    int newWidth = std::stoi(argv[3]);
    int newHeight = std::stoi(argv[4]);

    // 1. 画像の読み込み
    cv::Mat image = cv::imread(inputPath);
    if (image.empty()) {
        std::cerr << "エラー: 画像を開けませんでした: " << inputPath << std::endl;
        return -1;
    }

    // 2. リサイズ処理（cv::INTER_AREA は縮小時に画質が綺麗に保たれる設定です）
    cv::Mat resizedImage;
    cv::resize(image, resizedImage, cv::Size(newWidth, newHeight), 0, 0, cv::INTER_AREA);

    // 3. 画像の保存
    if (cv::imwrite(outputPath, resizedImage)) {
        std::cout << "成功: " << outputPath << " (" << newWidth << "x" << newHeight << ") に保存しました。\n";
    } else {
        std::cerr << "エラー: 画像の保存に失敗しました。" << std::endl;
        return -1;
    }

    return 0;
}
