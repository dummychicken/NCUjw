package com.ncu.examarrange.javaRunPython;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

//3失败->4成功

public class run3 {

    public static void main(String[] args) {
        try {
            //需传入的参数
//            String a = "123";
            System.out.println("start");
            //设置命令行传入参数python3 main.py --class_inf commonClass --outputFile commonClass.csv
            //String[] str = new String[] { "python", "src/main/java/com/ncu/examarrange/javaRunPython/npdemo1.py"};
            //String conf = "--class_inf", conf_inf = "classs_inf", out = "--outputFile", out_path = "commonClass.csv";,conf,conf_inf,out,out_path
            String[] str = new String[] { "python", "C:\\Users\\Tan\\Desktop\\GOODWORK\\jw\\NCUjw\\DDL\\preProcess.py"};
            Process pr = Runtime.getRuntime().exec(str);
            
            BufferedReader in = new BufferedReader(new InputStreamReader(pr.getInputStream(),"gbk"));
            String line;
            while ((line = in.readLine()) != null) {
                System.out.println(line);
            }
            in.close();
            pr.waitFor();
            System.out.println(pr.exitValue());
            System.out.println("end");
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
//        try{
//            System.out.println("start");
//            Process pr = Runtime.getRuntime().exec("E:\\anaconda3\\python E:\\git_workspace\\arrange\\src\\main\\java\\com\\ncu\\examarrange\\javaRunPython\\npdemo1.py");
//            BufferedReader in = new BufferedReader(new
//                    InputStreamReader(pr.getInputStream()));
//            String line;
//            while ((line = in.readLine()) != null) {
//                System.out.println(line);
//            }
//            in.close();
//            pr.waitFor();
//            System.out.println("end");
//        } catch (Exception e){
//            e.printStackTrace();
//        }
    }

}
