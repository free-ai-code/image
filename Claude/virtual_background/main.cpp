#include <opencv2/opencv.hpp>
#include <mediapipe/framework/calculator_framework.h>
#include <mediapipe/framework/port/parse_text_proto.h>
#include <mediapipe/framework/formats/image_frame.h>
#include <iostream>
#include <memory>

using namespace cv;
using namespace mediapipe;

class VirtualBackgroundProcessor {
private:
    Mat background_image;
    CalculatorGraph graph;
    
public:
    VirtualBackgroundProcessor(const std::string& background_path) {
        // 背景画像を読み込み
        background_image = imread(background_path);
        if (background_image.empty()) {
            throw std::runtime_error("Background image not found");
        }
    }
    
    // セグメンテーションパイプラインを初期化
    bool InitializeSegmentation() {
        // MediaPipeのセグメンテーショングラフ定義
        std::string calculator_graph_config_contents = R"(
            input_stream: "input_video"
            output_stream: "segmentation_mask"
            
            node {
              calculator: "FlowLimiterCalculator"
              input_stream: "input_video"
              input_stream: "FINISHED:segmentation_mask"
              output_stream: "throttled_input_video"
              options {
                [mediapipe.FlowLimiterCalculatorOptions.ext] {
                  max_in_flight: 1
                }
              }
            }
            
            node {
              calculator: "SelfieSegmentationGpu"
              input_stream: "IMAGE:throttled_input_video"
              output_stream: "SEGMENTATION_MASK:raw_segmentation"
              options {
                [mediapipe.SelfieSegmentationOptions.ext] {
                  model_selection: 1
                }
              }
            }
            
            node {
              calculator: "RecolorCalculator"
              input_stream: "IMAGE:throttled_input_video"
              input_stream: "MASK:raw_segmentation"
              output_stream: "segmentation_mask"
              options {
                [mediapipe.RecolorCalculatorOptions.ext] {
                  color {
                    r: 0
                    g: 0
                    b: 0
                  }
                }
              }
            }
        )";
        
        auto status = graph.Initialize(
            ParseTextProtoOrDie<CalculatorGraphConfig>(
                calculator_graph_config_contents));
        
        if (!status.ok()) {
            std::cerr << "Failed to initialize graph: " << status.message() << std::endl;
            return false;
        }
        
        return true;
    }
    
    // リアルタイム処理
    Mat ProcessFrame(const Mat& input_frame) {
        Mat frame_rgb;
        cvtColor(input_frame, frame_rgb, COLOR_BGR2RGB);
        
        // フレームサイズを背景と合わせる
        Mat bg_resized = background_image.clone();
        if (bg_resized.size() != frame_rgb.size()) {
            resize(bg_resized, bg_resized, frame_rgb.size());
        }
        
        // セグメンテーションマスクを取得（MediaPipe処理）
        Mat mask = GetSegmentationMask(frame_rgb);
        
        // マスクの平滑化（エッジを滑らかに）
        GaussianBlur(mask, mask, Size(11, 11), 0);
        
        // マスクを0-1の範囲に正規化
        Mat mask_normalized;
        mask.convertTo(mask_normalized, CV_32F, 1.0 / 255.0);
        
        // 背景合成（マスクベースのアルファブレンディング）
        Mat result = CompositeBackground(frame_rgb, bg_resized, mask_normalized);
        
        // RGBをBGRに戻す
        Mat output_bgr;
        cvtColor(result, output_bgr, COLOR_RGB2BGR);
        
        return output_bgr;
    }
    
private:
    // セグメンテーションマスクを取得（簡略版）
    Mat GetSegmentationMask(const Mat& frame) {
        // 実際の実装では、MediaPipeからの出力を使用
        // ここではプレースホルダー
        Mat mask = Mat::zeros(frame.size(), CV_8U);
        
        // 顔領域の粗い検出（OpenCVの顔検出器を使用）
        CascadeClassifier face_cascade(
            cv::samples::findFile(
                "haarcascade_frontalface_default.xml"));
        
        std::vector<Rect> faces;
        face_cascade.detectMultiScale(frame, faces, 1.1, 4);
        
        // 検出された顔の領域にマスクを描画
        for (const auto& face : faces) {
            // 顔領域を拡張して背景を含む
            Rect expanded = face + Size(50, 100);
            expanded &= Rect(0, 0, frame.cols, frame.rows);
            rectangle(mask, expanded, Scalar(255), -1);
            
            // エッジブレンディング用にぼかし
            GaussianBlur(mask(expanded), mask(expanded), Size(15, 15), 0);
        }
        
        return mask;
    }
    
    // 背景合成処理
    Mat CompositeBackground(const Mat& foreground, const Mat& background, 
                           const Mat& mask_normalized) {
        Mat result = foreground.clone();
        
        // アルファブレンディング
        for (int y = 0; y < foreground.rows; y++) {
            for (int x = 0; x < foreground.cols; x++) {
                float alpha = mask_normalized.at<float>(y, x);
                
                // 人物領域（alpha=1）は前景、背景（alpha=0）は背景画像
                Vec3b fg = foreground.at<Vec3b>(y, x);
                Vec3b bg = background.at<Vec3b>(y, x);
                
                result.at<Vec3b>(y, x) = Vec3b(
                    saturate_cast<uchar>(fg[0] * alpha + bg[0] * (1 - alpha)),
                    saturate_cast<uchar>(fg[1] * alpha + bg[1] * (1 - alpha)),
                    saturate_cast<uchar>(fg[2] * alpha + bg[2] * (1 - alpha))
                );
            }
        }
        
        return result;
    }
};

// メイン処理
int main() {
    try {
        // 背景画像を指定
        VirtualBackgroundProcessor processor("background.jpg");
        
        // Webカメラを開く
        VideoCapture cap(0);
        if (!cap.isOpened()) {
            std::cerr << "Cannot open camera" << std::endl;
            return -1;
        }
        
        // フレームサイズ設定
        cap.set(CAP_PROP_FRAME_WIDTH, 640);
        cap.set(CAP_PROP_FRAME_HEIGHT, 480);
        cap.set(CAP_PROP_FPS, 30);
        
        Mat frame, result;
        
        std::cout << "Press 'q' to quit" << std::endl;
        
        while (true) {
            cap >> frame;
            if (frame.empty()) break;
            
            // フレームを処理
            result = processor.ProcessFrame(frame);
            
            // 結果を表示
            imshow("Virtual Background", result);
            
            if (waitKey(1) == 'q') break;
        }
        
        cap.release();
        destroyAllWindows();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return -1;
    }
    
    return 0;
}
