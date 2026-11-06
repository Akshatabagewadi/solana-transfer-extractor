fn main() {
    let protoc = protoc_bin_vendored::protoc_bin_path().expect("protoc binary");
    std::env::set_var("PROTOC", protoc);

    prost_build::Config::new()
        .compile_protos(
            &["proto/solana.proto", "proto/transfers.proto"],
            &["proto"],
        )
        .expect("failed to compile protobuf files");

    println!("cargo:rerun-if-changed=proto/solana.proto");
    println!("cargo:rerun-if-changed=proto/transfers.proto");
}