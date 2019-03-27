package swyoo;
import java.io.File;

public class Tool {
	public void filedelete(String path) {
		File deleteFolder = new File(path);
		File[] deleteFolderList = deleteFolder.listFiles();
		for (int j = 0; j < deleteFolderList.length; ++j) {
			deleteFolderList[j].delete();
		}
		deleteFolder.delete();
	}
}
