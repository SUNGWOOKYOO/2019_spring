package SocialNetwork;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

public class SocialNetworkDriver extends Configured implements Tool {
	@Override
	public int run(String[] args) throws Exception {
		// TODO Auto-generated method stub
		if (args.length != 2) {
			System.out.println("Usage: [input] [output]");
			System.exit(-1);
		}

		// phase 1
		Job job = Job.getInstance(getConf());
		job.setJobName("SocialNetWork");
		job.setJarByClass(SocialNetworkDriver.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);
		job.setMapperClass(SocialNetworkMapper.class);
		job.setReducerClass(SocialNetworkReducer.class);
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);

		// file I.O setting
		Path inputFilePath = new Path(args[0]);
		Path outputFilePath = new Path("temp");
		FileInputFormat.addInputPath(job, inputFilePath);
		FileOutputFormat.setOutputPath(job, outputFilePath);

		// Phase 2
		Job job2 = Job.getInstance(getConf());
		job2.setJobName("Matrix Multiplication Two phase Version");
		job2.setJarByClass(SocialNetworkDriver.class);
		job2.setOutputKeyClass(Text.class);
		job2.setOutputValueClass(Text.class);
		job2.setMapperClass(SocialNetworkMapper2.class);
		job2.setReducerClass(SocialNetworkReducer2.class);
		job2.setInputFormatClass(TextInputFormat.class);
		job2.setOutputFormatClass(TextOutputFormat.class);
		job2.setNumReduceTasks(1);

		// Broadcasting
		Configuration config = job2.getConfiguration();
		config.setInt("k", 50);

		// file I.O setting
		Path inputFilePath2 = outputFilePath;
		Path outputFilePath2 = new Path(args[1]);
		FileInputFormat.addInputPath(job2, inputFilePath2);
		FileOutputFormat.setOutputPath(job2, outputFilePath2);

		// result file delete code
		FileSystem fs = FileSystem.newInstance(getConf());
		if (fs.exists(outputFilePath)) {
			fs.delete(outputFilePath, true);
		}
		FileSystem fs2 = FileSystem.newInstance(getConf());
		if (fs2.exists(outputFilePath2)) {
			fs2.delete(outputFilePath2, true);
		}

//		return job.waitForCompletion(true) ? 0 : 1;
		return (job.waitForCompletion(true) && job2.waitForCompletion(true)) ? 0 : 1;
	}

	public static void main(String[] args) throws Exception {
		SocialNetworkDriver test = new SocialNetworkDriver();
		int res = ToolRunner.run(test, args);
	}
}
